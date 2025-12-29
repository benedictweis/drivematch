package main

import (
	"context"
	"fmt"
	"sort"
	"strings"

	"github.com/benedictweis/drivematch/internal/data"
	"github.com/benedictweis/drivematch/internal/database"
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
			Name:   "vehicles",
			Usage:  "list saved vehicles",
			Action: listVehicles,
		},
		{
			Name:   "vehicles-no-info",
			Usage:  "list saved vehicles without information",
			Action: listVehiclesNoInfo,
		},
		{
			Name:   "cars-no-identifier",
			Usage:  "list cars from all searches without a key identifier",
			Action: listCarsNoIdentifier,
		},
	},
}

func listSearches(ctx context.Context, cmd *cli.Command) error {
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

func listVehicles(ctx context.Context, cmd *cli.Command) error {
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

	searches, err := db.GetAllVehicleInfos()
	if err != nil {
		return fmt.Errorf("error getting searches from database: %w", err)
	}

	columns := 4
	table := make([]string, (len(searches)+1)*columns)

	table[0] = "ID"
	table[1] = "Created At"
	table[2] = "Data Type"
	table[3] = "Data Length"

	for i, search := range searches {
		baseIdx := (i + 1) * columns
		table[baseIdx+0] = search.ID
		table[baseIdx+1] = search.CreatedAt.Format("2006-01-02 15:04:05")
		table[baseIdx+2] = search.DataType
		table[baseIdx+3] = output.DataLength(len(search.Data))
	}

	outputWriter.WriteTable(columns, table)

	return nil
}

func listVehiclesNoInfo(ctx context.Context, cmd *cli.Command) error {
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

	missingKeyIdentifiers, err := data.GetMissingKeyIdentifiers(db)
	if err != nil {
		return fmt.Errorf("error getting missing key identifiers: %w", err)
	}

	sort.Strings(missingKeyIdentifiers)

	missingKeyIdentifiersWithLink := make([]string, len(missingKeyIdentifiers))
	for i, id := range missingKeyIdentifiers {
		searchPart := strings.Replace(id, "/", "-", 1)
		link := fmt.Sprintf("http://www.hsn-tsn.de/%s.html", searchPart)
		missingKeyIdentifiersWithLink[i] = output.Link(link, id)
	}

	var table []string
	table = append([]string{"Identifier"}, missingKeyIdentifiersWithLink...)

	outputWriter.WriteTable(1, table)

	return nil
}

func listCarsNoIdentifier(ctx context.Context, cmd *cli.Command) error {
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

	_ = outputWriter

	return nil
}
