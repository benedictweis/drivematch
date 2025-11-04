package main

import (
	"fmt"
	"os"
	"sort"

	"github.com/benedictweis/drivematch/internal/analysis"
	"github.com/benedictweis/drivematch/internal/common"
	"github.com/benedictweis/drivematch/internal/data"
	"github.com/olekukonko/tablewriter"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: drivematch <filename>")
		os.Exit(1)
	}

	filename := os.Args[1]

	content, err := os.ReadFile(filename)
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		os.Exit(1)
	}

	cars, err := data.GetCarsFromMobileDeData(content)
	if err != nil {
		fmt.Printf("Error parsing car data: %v\n", err)
		os.Exit(1)
	}

	scores := analysis.ScoreCars(cars, 1.0, -1.0, -1.0, 0.0)

	type CarScore struct {
		Car   *common.Car
		Score float64
	}

	carScores := make([]CarScore, len(cars))
	for i := range cars {
		carScores[i] = CarScore{Car: &cars[i], Score: scores[i]}
	}

	sort.Slice(carScores, func(i, j int) bool {
		return carScores[i].Score > carScores[j].Score
	})

	table := tablewriter.NewWriter(os.Stdout)
	table.Header([]string{"ID", "Make", "Model", "Year", "Mileage", "Price", "Horsepower", "Fuel Type"})

	for _, cs := range carScores {
		month := cs.Car.FirstRegistration.Month()
		year := cs.Car.FirstRegistration.Year()
		mileage := fmt.Sprintf("%.0f km", cs.Car.Mileage)
		price := fmt.Sprintf("%.0f EUR", cs.Car.Price)
		horsepower := fmt.Sprintf("%.0f hp", cs.Car.HorsePower)

		table.Append([]string{
			clickableLink(cs.Car.ListingURL, cs.Car.ID),
			cs.Car.Manufacturer,
			cs.Car.Model,
			fmt.Sprintf("%02d/%d", month, year),
			mileage,
			price,
			horsepower,
			cs.Car.FuelType,
		})
	}

	table.Render()
}

func clickableLink(url, text string) string {
	return fmt.Sprintf("\033]8;;%s\033\\%s\033]8;;\033\\\n", url, text)
}
