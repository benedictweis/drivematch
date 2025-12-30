package main

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"

	"github.com/benedictweis/drivematch/internal/data"
	"github.com/benedictweis/drivematch/internal/database"
	"github.com/benedictweis/drivematch/internal/scraping"
	"github.com/urfave/cli/v3"
)

var scrapeAdacCmd *cli.Command = &cli.Command{
	Name:      "scrape-adac",
	Usage:     "Scrape missing vehicle information from all unique cars across all searches using ADAC car data",
	UsageText: "drivematch scrape-adac [options] <urls>",
	Action:    scrapeAdac,
	Arguments: []cli.Argument{
		&cli.StringArg{
			Name:        "urls",
			Destination: &searchURL,
		},
	},
}

func scrapeAdac(ctx context.Context, cmd *cli.Command) error {
	db := database.NewSQLiteDatabase(databasePath)

	if err := db.Connect(); err != nil {
		return fmt.Errorf("error connecting to database: %w", err)
	}
	defer db.Close()

	misingKeyIdentifiers, err := data.GetMissingKeyIdentifiers(db)
	if err != nil {
		return fmt.Errorf("error getting missing key identifiers: %w", err)
	}

	var keywords []string

	if searchURL != "" {
		keywords = strings.Split(searchURL, ",")
	} else {
		var keyIdentifierList []string
		for _, keyIdentifier := range misingKeyIdentifiers {
			if keyIdentifier != "" {
				if keyIdentifier == "/" {
					continue // Skip malformed identifier
				}

				// If key identifier contains a slash, format it as "HSN [part1] TSN [part2]"
				if parts := strings.Split(keyIdentifier, "/"); len(parts) == 2 {
					keyIdentifier = fmt.Sprintf("HSN \"%s\" TSN \"%s\"", parts[0], parts[1])
				}
			}
			keyIdentifierList = append(keyIdentifierList, keyIdentifier)
		}

		keywords = keyIdentifierList
	}

	fmt.Printf("%d vehicles left to scrape\n", len(keywords))

	adacData, err := scraping.ScrapeADAC(keywords)
	if err != nil {
		return fmt.Errorf("error scraping ADAC data: %w", err)
	}

	var results []json.RawMessage
	if err := json.Unmarshal(adacData, &results); err != nil {
		return fmt.Errorf("error unmarshaling output from 'adac': %w", err)
	}

	for _, result := range results {
		var dataMap map[string]string
		if err := json.Unmarshal(result, &dataMap); err != nil {
			return fmt.Errorf("error unmarshaling result for %w", err)
		}

		keyNumber := fmt.Sprintf("%s/%s", dataMap[data.HSNKey], dataMap[data.TSNKey])

		err := db.InsertVehicleInfo(keyNumber, "adac", result)
		if err != nil {
			fmt.Printf("error inserting vehicle info for key %s: %v\n", keyNumber, err)
			continue
		}

		if tsn2, exists := dataMap[data.TSN2Key]; exists && tsn2 != "" {
			keyNumber2 := fmt.Sprintf("%s/%s", dataMap[data.HSNKey], tsn2)
			err := db.InsertVehicleInfo(keyNumber2, "adac", result)
			if err != nil {
				fmt.Printf("error inserting vehicle info for key %s: %v\n", keyNumber2, err)
			}
		}
	}

	fmt.Println("Scrape of vehicle information completed")

	return nil
}
