package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"strconv"
	"strings"

	"github.com/benedictweis/drivematch/internal/scraping"
	"github.com/urfave/cli/v3"
)

var (
	searchName string
	searchURL  string

	adacScrapeFile string
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

	adacScrapeTargets, err := scraping.ParseADACScrapeFile(content)
	if err != nil {
		return fmt.Errorf("error parsing adac scrape file: %w", err)
	}

	adacScrapeResult, err := scraping.ScrapeADAC(adacScrapeTargets)
	if err != nil {
		return fmt.Errorf("error scraping adac.de: %w", err)
	}

	for _, result := range adacScrapeResult {
		urlParts := strings.Split(result.URL, "/")
		provider_id := urlParts[len(urlParts)-2]

		_, err := strconv.Atoi(provider_id)
		if err != nil {
			fmt.Fprintf(os.Stderr, "error on provider id format, skipping non-numeric id: %s\n", provider_id)
			continue
		}

		jsonData, err := json.Marshal(result.Data)
		if err != nil {
			fmt.Fprintf(os.Stderr, "error marshaling adac data to json: %w", err)
			continue
		}

		_, err = db.InsertCarDetail(provider_id, result.CarHash, "adac", jsonData)
		if err != nil {
			fmt.Fprintf(os.Stderr, "error inserting car detail into database: %w", err)
		}
	}

	fmt.Println("Scrape completed")
	return nil
}
