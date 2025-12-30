package main

import (
	"context"
	"fmt"
	"sort"

	"github.com/benedictweis/drivematch/internal/analysis"
	"github.com/benedictweis/drivematch/internal/output"
	"github.com/benedictweis/drivematch/internal/scraping"
	"github.com/benedictweis/drivematch/internal/types"
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

	cars := make([]types.Car, 0)
	for _, searchData := range searches {
		searchCars, err := scraping.GetCarsFromMobileDeData(searchData)
		if err != nil {
			return fmt.Errorf("error parsing car data: %w", err)
		}
		cars = append(cars, searchCars...)
	}

	uniqueCars := analysis.GetUniqueCars(cars)

	sort.Slice(uniqueCars, func(i, j int) bool {
		return uniqueCars[i].Amount > uniqueCars[j].Amount
	})

	columns := 8
	table := make([]string, (len(uniqueCars)+1)*columns)

	table[0] = "Hash"
	table[1] = "Count"
	table[2] = "Manufacturer"
	table[3] = "Model"
	table[4] = "Year From"
	table[5] = "Year To"
	table[6] = "Horsepower"
	table[7] = "Fuel Type"

	for i, g := range uniqueCars {
		baseIdx := (i + 1) * columns
		table[baseIdx+0] = g.Hash
		table[baseIdx+1] = fmt.Sprintf("%d", g.Amount)
		table[baseIdx+2] = g.Manufacturer
		table[baseIdx+3] = g.Model
		table[baseIdx+4] = fmt.Sprintf("%d", g.YearFrom)
		table[baseIdx+5] = fmt.Sprintf("%d", g.YearTo)
		table[baseIdx+6] = fmt.Sprintf("%.0f hp", g.HorsePower)
		table[baseIdx+7] = g.FuelType
	}

	outputWriter.WriteTable(columns, table)
	return nil
}
