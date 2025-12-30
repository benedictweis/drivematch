package main

import (
	"context"
	"fmt"

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

	return nil
}
