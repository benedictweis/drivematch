package main

import (
	"context"
	"fmt"

	"github.com/benedictweis/drivematch/internal/output"
	"github.com/urfave/cli/v3"
)

var listCmd *cli.Command = &cli.Command{
	Name:      "list",
	Usage:     "list searches or vehicle information stored in the database",
	UsageText: "drivematch list",
	Commands: []*cli.Command{
		{
			Name:   "searches",
			Usage:  "list saved searches",
			Action: listSearches,
		},
		{
			Name:   "cars",
			Usage:  "list unique cars identified across all searches",
			Action: listCars,
		},
	},
}

func listSearches(ctx context.Context, cmd *cli.Command) error {
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

func listCars(ctx context.Context, cmd *cli.Command) error {
	searches, err := db.GetAllSearchData()
	if err != nil {
		return fmt.Errorf("error getting searches from database: %w", err)
	}

	_ = searches

	return nil
}
