package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/benedictweis/drivematch/internal/scraping"
	"github.com/urfave/cli/v3"
)

var (
	databasePath string
	searchName   string
	searchURL    string
	searchId     string
	sortBy       string
	outputFormat string

	weightPrice      float64
	weightHorsepower float64
	weightMileage    float64
	weightAge        float64
)

var cmd *cli.Command = &cli.Command{
	Name:  "drivematch",
	Usage: "A tool to scrape, analyze and group car listings from mobile.de",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:        "database-path",
			Usage:       "Path to the SQLite database file",
			Value:       "drivematch.db",
			Aliases:     []string{"d"},
			Destination: &databasePath,
		},
		&cli.StringFlag{
			Name:        "output-format",
			Usage:       "Output format: 'table', 'csv' or 'grep'",
			Value:       "table",
			Aliases:     []string{"o"},
			Destination: &outputFormat,
		},
	},
	Commands: []*cli.Command{
		scrapeCmd,
		scrapeAdacCmd,
		listCmd,
		scoreCmd,
		groupCmd,
		getCmd,
	},
}

func main() {
	if err := scraping.ExtractMobiledeScraper(); err != nil {
		fmt.Println("error extracting mobile.de scraper:", err)
		os.Exit(1)
	}

	if err := cmd.Run(context.Background(), os.Args); err != nil {
		log.Fatal(err)
	}
}
