package main

import (
	"context"
	"fmt"

	"github.com/benedictweis/drivematch/internal/database"
	"github.com/benedictweis/drivematch/internal/output"
	"github.com/urfave/cli/v3"
)

var listCmd *cli.Command = &cli.Command{
	Name:      "list",
	Usage:     "list searches",
	UsageText: "drivematch list",
	Action:    list,
}

func list(ctx context.Context, cmd *cli.Command) error {
	outputWriter, err := output.GetOutputWriter(outputFormat)
	if err != nil {
		fmt.Println(err.Error())
		return cli.ShowSubcommandHelp(cmd)
	}

	db := database.NewSQLiteDatabase(databasePath)

	if err := db.Connect(); err != nil {
		return fmt.Errorf("error connecting to database: %w", err)
	}
	defer db.Close()

	searches, err := db.GetSearches()
	if err != nil {
		return fmt.Errorf("error getting searches from database: %w", err)
	}

	columns := 5
	table := make([]string, (len(searches)+1)*columns)

	table[0] = "ID"
	table[1] = "Name"
	table[2] = "Created At"
	table[3] = "Search Type"
	table[4] = "Data Length"

	for i, search := range searches {
		baseIdx := (i + 1) * columns
		table[baseIdx+0] = search.ID
		table[baseIdx+1] = search.Name
		table[baseIdx+2] = search.CreatedAt.Format("2006-01-02 15:04:05")
		table[baseIdx+3] = search.SearchType
		table[baseIdx+4] = output.DataLength(search.DataLen)
	}

	outputWriter.WriteTable(columns, table)

	return nil
}
