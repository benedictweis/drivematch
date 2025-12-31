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
	searchId string

	weightPrice      float64
	weightHorsepower float64
	weightMileage    float64
	weightAge        float64
)

var scoreCmd *cli.Command = &cli.Command{
	Name:      "score",
	Usage:     "Score cars from a previous search",
	UsageText: "drivematch score [options] <searchId>",
	Flags:     scoreFlags,
	Arguments: []cli.Argument{
		&cli.StringArg{
			Name:        "searchId",
			Destination: &searchId,
			UsageText:   "the ID of the search to score cars from",
		},
	},
	Action: score,
}

var scoreFlags []cli.Flag = []cli.Flag{
	&cli.FloatFlag{
		Name:        "weight-horsepower",
		Aliases:     []string{"wh"},
		Usage:       "weight for horsepower scoring",
		Destination: &weightHorsepower,
		Value:       1.0,
	},
	&cli.FloatFlag{
		Name:        "weight-price",
		Aliases:     []string{"wp"},
		Usage:       "weight for price scoring",
		Destination: &weightPrice,
		Value:       -1.0,
	},
	&cli.FloatFlag{
		Name:        "weight-mileage",
		Aliases:     []string{"wm"},
		Usage:       "weight for mileage scoring",
		Destination: &weightMileage,
		Value:       -1.0,
	},
	&cli.FloatFlag{
		Name:        "weight-age",
		Aliases:     []string{"wa"},
		Usage:       "weight for age scoring",
		Destination: &weightAge,
		Value:       -1.0,
	},
}

func score(ctx context.Context, cmd *cli.Command) error {
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

	carDetailsEntries, err := db.GetAllCarDetails()
	if err != nil {
		return fmt.Errorf("error getting car details from database: %w", err)
	}

	vehicleInfos := make(map[string][]*types.VehicleInfo)
	for _, cd := range carDetailsEntries {
		vi, err := scraping.GetVehicleInfoFromADACData(&cd)
		if err != nil {
			return fmt.Errorf("error parsing ADAC vehicle info: %w", err)
		}
		vehicleInfos[vi.CarHash] = append(vehicleInfos[vi.CarHash], vi)
	}

	for i := range cars {
		analysis.MapCarToVehicleInfo(&cars[i], vehicleInfos)
	}

	scores := analysis.ScoreCars(cars, weightHorsepower, weightPrice, weightMileage, weightAge)

	type CarScore struct {
		Car   *types.Car
		Score float64
	}

	carScores := make([]CarScore, len(cars))
	for i := range cars {
		carScores[i] = CarScore{Car: &cars[i], Score: scores[i]}
	}

	sort.Slice(carScores, func(i, j int) bool {
		return carScores[i].Score > carScores[j].Score
	})

	columns := 14
	table := make([]string, (len(carScores)+1)*columns)

	table[0] = "ID"
	table[1] = "Make"
	table[2] = "Model"
	table[3] = "Year"
	table[4] = "Mileage"
	table[5] = "Price"
	table[6] = "Horsepower"
	table[7] = "Fuel Type"
	table[8] = "Torque"
	table[9] = "Trunk Volume"
	table[10] = "0-100 km/h"
	table[11] = "Top Speed"
	table[12] = "Noise Level"
	table[13] = "Consumption"

	for i, cs := range carScores {
		month := cs.Car.FirstRegistration.Month()
		year := cs.Car.FirstRegistration.Year()

		baseIdx := (i + 1) * columns
		table[baseIdx+0] = output.Link(cs.Car.ListingURL, cs.Car.ID)
		table[baseIdx+1] = cs.Car.Manufacturer
		if cs.Car.VehicleInfo != nil {
			table[baseIdx+2] = output.Link(cs.Car.VehicleInfo.DetailsURL, cs.Car.Model)
		} else {
			table[baseIdx+2] = cs.Car.Model
		}
		table[baseIdx+3] = fmt.Sprintf("%02d/%d", month, year)
		table[baseIdx+4] = fmt.Sprintf("%.0f km", cs.Car.Mileage)
		table[baseIdx+5] = output.Price(cs.Car.Price)
		table[baseIdx+6] = fmt.Sprintf("%.0f hp", cs.Car.HorsePower)
		table[baseIdx+7] = cs.Car.FuelType
		if cs.Car.VehicleInfo != nil {
			table[baseIdx+8] = fmt.Sprintf("%.0f Nm", cs.Car.VehicleInfo.Torque)
			table[baseIdx+9] = fmt.Sprintf("%d l", cs.Car.VehicleInfo.TrunkVolume)
			table[baseIdx+10] = fmt.Sprintf("%.2f s", cs.Car.VehicleInfo.Acceleration0to100)
			table[baseIdx+11] = fmt.Sprintf("%d km/h", cs.Car.VehicleInfo.TopSpeed)
			table[baseIdx+12] = fmt.Sprintf("%.0f dB", cs.Car.VehicleInfo.NoiseLevel)
			table[baseIdx+13] = cs.Car.VehicleInfo.FuelConsumption
		} else {
			table[baseIdx+8] = ""
			table[baseIdx+9] = ""
			table[baseIdx+10] = ""
			table[baseIdx+11] = ""
			table[baseIdx+12] = ""
			table[baseIdx+13] = ""
		}
	}

	outputWriter.WriteTable(columns, table)
	return nil
}
