package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/benedictweis/drivematch/internal/database"
	"github.com/benedictweis/drivematch/internal/output"
	"github.com/urfave/cli/v3"
)

var (
	databasePath string
	outputFormat string

	db           *database.SQLiteDatabase
	outputWriter output.OutputWriter
)

var cmd *cli.Command = &cli.Command{
	Name:  "drivematch",
	Usage: "A tool to analyse offerings on the used car market",
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
	Before: handleBefore,
	Commands: []*cli.Command{
		scrapeCmd,
		listCmd,
		scoreCmd,
		groupCmd,
		getCmd,
	},
	After: handleAfter,
}

func main() {
	if err := cmd.Run(context.Background(), os.Args); err != nil {
		log.Fatal(err)
	}
}

func handleBefore(ctx context.Context, cmd *cli.Command) (context.Context, error) {
	err := setupDatabase(databasePath)
	if err != nil {
		return ctx, err
	}

	err = setupOutput(outputFormat)
	if err != nil {
		return ctx, err
	}

	return ctx, nil
}

func handleAfter(ctx context.Context, cmd *cli.Command) error {
	db.Close()
	return nil
}

func setupDatabase(dbPath string) error {
	db = database.NewSQLiteDatabase(dbPath)

	if err := db.Connect(); err != nil {
		return fmt.Errorf("error connecting to database: %w", err)
	}

	return nil
}

func setupOutput(format string) error {
	var err error
	outputWriter, err = output.GetOutputWriter(format)
	if err != nil {
		return fmt.Errorf("error setting up output writer: %w", err)
	}

	return nil
}
