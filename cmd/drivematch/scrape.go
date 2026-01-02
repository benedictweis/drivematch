package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"

	"github.com/benedictweis/drivematch/internal/scraping"
	"github.com/urfave/cli/v3"
)

var (
	searchName string
	searchURL  string

	adacScrapeFile   string
	adacLookupHSNTSN bool
)

var scrapeCmd *cli.Command = &cli.Command{
	Name:      "scrape",
	Usage:     "Scrape car data from a mobile.de url",
	UsageText: "drivematch scrape",
	Commands: []*cli.Command{
		{
			Name:      "mobilede",
			Usage:     "Scrape use car listings from mobile.de",
			UsageText: "drivematch scrape mobilede [options] <name> <url>",
			Arguments: []cli.Argument{
				&cli.StringArg{
					Name:        "name",
					Destination: &searchName,
				},
				&cli.StringArg{
					Name:        "url",
					Destination: &searchURL,
				},
			},
			Action: scrapeMobileDe,
		},
		{
			Name:      "adac",
			Usage:     "Scrape supplementary car data from adac.de",
			UsageText: "drivematch scrape adac [options] <file>",
			Arguments: []cli.Argument{
				&cli.StringArg{
					Name:        "file",
					Destination: &adacScrapeFile,
				},
			},
			Flags: []cli.Flag{
				&cli.BoolFlag{
					Name:        "lookup-hsn-tsn",
					Aliases:     []string{"l"},
					Usage:       "Resolves hsn and tsn numbers to a car name which is then used to find the correct car on adac.de",
					Destination: &adacLookupHSNTSN,
					Value:       false,
				},
			},
			Action: scrapeADAC,
		},
	},
}

func scrapeMobileDe(ctx context.Context, cmd *cli.Command) error {
	if searchURL == "" || searchName == "" {
		return fmt.Errorf("both search name and url must be provided")
	}

	searchData, err := scraping.ScrapeMobileDe(searchURL)
	if err != nil {
		return fmt.Errorf("error scraping mobile.de: %w", err)
	}

	searchId, err := db.InsertSearch(searchName, "mobilede", searchData)
	if err != nil {
		return fmt.Errorf("error inserting search into database: %w", err)
	}

	fmt.Printf("Scrape completed (id: %s)\n", searchId)
	return nil
}

func scrapeADAC(ctx context.Context, cmd *cli.Command) error {
	if adacScrapeFile == "" {
		return fmt.Errorf("scrape file must be provided")
	}

	if _, err := os.Stat(adacScrapeFile); os.IsNotExist(err) {
		return fmt.Errorf("scrape file does not exist: %s", adacScrapeFile)
	}

	content, err := os.ReadFile(adacScrapeFile)
	if err != nil {
		return fmt.Errorf("error reading file: %w", err)
	}

	adacScrapeTargets, err := scraping.ParseADACScrapeFile(content, adacLookupHSNTSN)
	if err != nil {
		return fmt.Errorf("error parsing adac scrape file: %w", err)
	}

	adacScrapeResult, err := scraping.ScrapeADAC(adacScrapeTargets)
	if err != nil {
		return fmt.Errorf("error scraping adac.de: %w", err)
	}

	for _, result := range adacScrapeResult {
		jsonData, err := json.Marshal(result.Data)
		if err != nil {
			return fmt.Errorf("error marshaling result data to JSON: %w", err)
		}

		carDetails, err := scraping.GetCarDetailsFromADACData(jsonData)
		if err != nil {
			fmt.Printf("error getting car details from ADAC data: %w\n", err)
			continue
		}

		if carDetails.HSN == "" || carDetails.TSN == "" {
			fmt.Println("skipping car detail insert due to missing HSN/TSN")
			continue
		}

		_, err = db.InsertCarDetail(carDetails.HSN, carDetails.TSN, "adac", jsonData)
		if err != nil {
			fmt.Printf("error inserting car details into database: %v\n", err)
			continue
		}
	}

	fmt.Println("Scrape completed")
	return nil
}
