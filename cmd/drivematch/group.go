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
			Usage:       "Sort groups by 'score', 'count' or 'hsntsn'",
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
		return fmt.Errorf("searchId must be provided")
	}

	searchData, err := db.GetSearchData(searchId)
	if err != nil {
		return fmt.Errorf("error getting search data from database: %w", err)
	}

	cars, err := scraping.GetCarsFromMobileDeData(searchData)
	if err != nil {
		return fmt.Errorf("error parsing car data: %w", err)
	}

	carDetails, err := db.GetAllCarDetails()
	if err != nil {
		return fmt.Errorf("error getting car details from database: %w", err)
	}

	carDetailMap := make(map[types.UniqueCarGroup]*types.CarDetails)
	for _, cd := range carDetails {
		carDetails, err := scraping.GetCarDetailsFromADACData(cd.Data)
		if err != nil {
			return fmt.Errorf("error parsing car detail data: %w", err)
		}

		uc := types.UniqueCarGroup{
			HSN: carDetails.HSN,
			TSN: carDetails.TSN,
		}

		carDetailMap[uc] = carDetails
	}

	scores := analysis.ScoreCars(cars, weightPrice, weightHorsepower, weightMileage, weightAge)
	groups := analysis.GroupCars(cars, scores, carDetailMap)

	switch sortBy {
	case "count":
		sort.Slice(groups, func(i, j int) bool {
			return groups[i].Amount > groups[j].Amount
		})
	case "hsntsn":
		sort.Slice(groups, func(i, j int) bool {
			if groups[i].HSN != groups[j].HSN {
				return groups[i].HSN < groups[j].HSN
			}
			return groups[i].TSN < groups[j].TSN
		})
	default:
		sort.Slice(groups, func(i, j int) bool {
			return groups[i].AverageScore > groups[j].AverageScore
		})
	}

	columns := 16
	table := make([]string, (len(groups)+1)*columns)

	table[0] = "HSN"
	table[1] = "TSN"
	table[2] = "Count"
	table[3] = "Make"
	table[4] = "Model"
	table[5] = "Avg. Age"
	table[6] = "Avg. Mileage"
	table[7] = "Avg. Price"
	table[8] = "Fuel"
	table[9] = "Horsepower"
	table[10] = "Torque"
	table[11] = "Trunk"
	table[12] = "0-100"
	table[13] = "Top Speed"
	table[14] = "Noise Level"
	table[15] = "Consumption"

	for i, group := range groups {
		baseIdx := (i + 1) * columns
		table[baseIdx+0] = group.HSN
		table[baseIdx+1] = group.TSN
		table[baseIdx+2] = fmt.Sprintf("%d", group.Amount)
		table[baseIdx+3] = group.Manufacturer
		if group.CarDetails != nil {
			table[baseIdx+4] = output.Link(group.CarDetails.DetailsURL, group.CarDetails.Model)
		} else {
			table[baseIdx+4] = group.Model
		}
		table[baseIdx+5] = fmt.Sprintf("%.0f", group.AverageAge)
		table[baseIdx+6] = fmt.Sprintf("%.0f km", group.AverageMileage)
		table[baseIdx+7] = output.Price(group.AveragePrice)
		table[baseIdx+8] = group.FuelType
		table[baseIdx+9] = fmt.Sprintf("%.0f hp", group.HorsePower)
		if group.CarDetails != nil {
			table[baseIdx+10] = fmt.Sprintf("%.0f Nm", group.CarDetails.Torque)
			table[baseIdx+11] = fmt.Sprintf("%d l", group.CarDetails.TrunkVolume)
			table[baseIdx+12] = fmt.Sprintf("%.2f s", group.CarDetails.Acceleration0to100)
			table[baseIdx+13] = fmt.Sprintf("%d km/h", group.CarDetails.TopSpeed)
			table[baseIdx+14] = fmt.Sprintf("%.0f dB", group.CarDetails.NoiseLevel)
			table[baseIdx+15] = group.CarDetails.FuelConsumption
		} else {
			table[baseIdx+10] = ""
			table[baseIdx+11] = ""
			table[baseIdx+12] = ""
			table[baseIdx+13] = ""
			table[baseIdx+14] = ""
			table[baseIdx+15] = ""
		}
	}

	outputWriter.WriteTable(columns, table)
	return nil
}
