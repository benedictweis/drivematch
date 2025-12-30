package main

import (
	"context"
	"fmt"
	"sort"

	"github.com/benedictweis/drivematch/internal/analysis"
	"github.com/benedictweis/drivematch/internal/output"
	"github.com/benedictweis/drivematch/internal/scraping"
	"github.com/urfave/cli/v3"
)

var (
	sortBy string
)

var groupCmd *cli.Command = &cli.Command{
	Name:      "group",
	Usage:     "Show car groups contained in a data file",
	UsageText: "drivematch group [options] <searchId>",
	Flags: append([]cli.Flag{
		&cli.StringFlag{
			Name:        "sort-by",
			Usage:       "Sort groups by 'score' or 'count'",
			Value:       "score",
			Aliases:     []string{"s"},
			Destination: &sortBy,
		},
	}, scoreFlags...),
	Arguments: []cli.Argument{
		&cli.StringArg{
			Name:        "searchId",
			Destination: &searchId,
		},
	},
	Action: group,
}

func group(ctx context.Context, cmd *cli.Command) error {
	if searchId == "" {
		fmt.Println("searchId must be provided")
		return cli.ShowSubcommandHelp(cmd)
	}

	searchData, err := db.GetSearchData(searchId)
	if err != nil {
		return fmt.Errorf("error getting search data from database: %w", err)
	}

	cars, err := scraping.GetCarsFromMobileDeData(searchData)
	if err != nil {
		return fmt.Errorf("error parsing car data: %w", err)
	}

	scores := analysis.ScoreCars(cars, weightPrice, weightHorsepower, weightMileage, weightAge)
	groups := analysis.GroupCars(cars, scores)

	switch sortBy {
	case "count":
		sort.Slice(groups, func(i, j int) bool {
			return groups[i].Amount > groups[j].Amount
		})
	default:
		sort.Slice(groups, func(i, j int) bool {
			return groups[i].AverageScore > groups[j].AverageScore
		})
	}

	columns := 8
	table := make([]string, (len(groups)+1)*columns)

	table[0] = "Make"
	table[1] = "Model"
	table[2] = "Count"
	table[3] = "Avg Age"
	table[4] = "Avg Mileage"
	table[5] = "Avg Price"
	table[6] = "Avg Horsepower"
	table[7] = "Fuel Type"

	for i, g := range groups {
		baseIdx := (i + 1) * columns
		table[baseIdx+0] = g.Manufacturer
		table[baseIdx+1] = g.Model
		table[baseIdx+2] = fmt.Sprintf("%d", g.Amount)
		table[baseIdx+3] = fmt.Sprintf("%.2f", g.AverageAge)
		table[baseIdx+4] = fmt.Sprintf("%.0f km", g.AverageMileage)
		table[baseIdx+5] = output.Price(g.AveragePrice)
		table[baseIdx+6] = fmt.Sprintf("%.0f hp", g.AverageHorsePower)
		table[baseIdx+7] = g.FuelType
	}

	outputWriter.WriteTable(columns, table)
	return nil
}
