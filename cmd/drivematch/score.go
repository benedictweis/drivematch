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

	columns := 8
	table := make([]string, (len(carScores)+1)*columns)

	table[0] = "ID"
	table[1] = "Make"
	table[2] = "Model"
	table[3] = "Year"
	table[4] = "Mileage"
	table[5] = "Price"
	table[6] = "Horsepower"
	table[7] = "Fuel Type"

	for i, cs := range carScores {
		month := cs.Car.FirstRegistration.Month()
		year := cs.Car.FirstRegistration.Year()

		baseIdx := (i + 1) * columns
		table[baseIdx+0] = output.Link(cs.Car.ListingURL, cs.Car.ID)
		table[baseIdx+1] = cs.Car.Manufacturer
		table[baseIdx+2] = cs.Car.Model
		table[baseIdx+3] = fmt.Sprintf("%02d/%d", month, year)
		table[baseIdx+4] = fmt.Sprintf("%.0f km", cs.Car.Mileage)
		table[baseIdx+5] = output.Price(cs.Car.Price)
		table[baseIdx+6] = fmt.Sprintf("%.0f hp", cs.Car.HorsePower)
		table[baseIdx+7] = cs.Car.FuelType
	}

	outputWriter.WriteTable(columns, table)
	return nil
}
