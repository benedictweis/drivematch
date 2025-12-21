package main

import (
	"context"
	"encoding/base64"
	"fmt"
	"os/exec"

	"github.com/benedictweis/drivematch/internal/database"
	"github.com/benedictweis/drivematch/internal/scraping"
	"github.com/urfave/cli/v3"
)

var scrapeCmd *cli.Command = &cli.Command{
	Name:      "scrape",
	Usage:     "Scrape car data from a mobile.de url",
	UsageText: "drivematch scrape [options] <name> <url>",
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
	Action: scrape,
}

func scrape(ctx context.Context, cmd *cli.Command) error {
	if searchURL == "" || searchName == "" {
		fmt.Println("both search name and url must be provided")
		return cli.ShowSubcommandHelp(cmd)
	}

	db := database.NewSQLiteDatabase(databasePath)

	if err := db.Connect(); err != nil {
		return fmt.Errorf("error connecting to database: %w", err)
	}
	defer db.Close()

	encodedURL := base64.StdEncoding.EncodeToString([]byte(searchURL))
	mobiledeCmd := exec.Command(scraping.MobileDeBinaryPath(), encodedURL)

	output, err := mobiledeCmd.Output()
	if err != nil {
		return fmt.Errorf("error capturing output from 'mobilede': %w", err)
	}

	searchId, err := db.InsertSearch(searchName, "mobilede", output)
	if err != nil {
		return fmt.Errorf("error inserting search into database: %w", err)
	}

	fmt.Printf("Scrape completed (id: %s)\n", searchId)

	return nil
}
