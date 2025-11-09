package main

import (
	"context"
	"encoding/base64"
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"sort"

	"github.com/benedictweis/drivematch/internal/analysis"
	"github.com/benedictweis/drivematch/internal/common"
	"github.com/benedictweis/drivematch/internal/data"
	"github.com/olekukonko/tablewriter"
	"github.com/urfave/cli/v3"
)

var (
	url    string
	file   string
	sortBy string
)

var cmd *cli.Command = &cli.Command{
	Name:  "drivematch",
	Usage: "A tool to scrape, analyze and group car listings from mobile.de",
	Commands: []*cli.Command{
		{
			Name:  "scrape",
			Usage: "Scrape car data from a mobile.de url",
			Arguments: []cli.Argument{
				&cli.StringArg{
					Name:        "url",
					Destination: &url,
				},
				&cli.StringArg{
					Name:        "file",
					Destination: &file,
				},
			},
			Action: scrape,
		},
		{
			Name:  "score",
			Usage: "Score cars contained in a data file",
			Arguments: []cli.Argument{
				&cli.StringArg{
					Name:        "file",
					Destination: &file,
				},
			},
			Action: score,
		},
		{
			Name:  "group",
			Usage: "Show car groups contained in a data file",
			Arguments: []cli.Argument{
				&cli.StringArg{
					Name:        "file",
					Destination: &file,
				},
			},
			Flags: []cli.Flag{
				&cli.StringFlag{
					Name:        "sort-by",
					Usage:       "Sort groups by 'score' or 'count'",
					Value:       "score",
					Aliases:     []string{"s"},
					Destination: &sortBy,
				},
			},
			Action: group,
		},
	},
}

func main() {
	if err := cmd.Run(context.Background(), os.Args); err != nil {
		log.Fatal(err)
	}
}

func scrape(ctx context.Context, cmd *cli.Command) error {
	executablePath, err := os.Executable()
	if err != nil {
		return fmt.Errorf("error getting executable path: %w", err)
	}

	dir := os.DirFS(filepath.Dir(executablePath))
	mobileDeFile := "mobilede"
	filePath := fmt.Sprintf("%s/%s", dir, mobileDeFile)

	info, err := os.Stat(filePath)
	if err != nil {
		return fmt.Errorf("error getting file info: %w", err)
	}

	if info.Mode()&0111 == 0 {
		return fmt.Errorf("file 'mobilede' is not executable")
	}

	encodedURL := base64.StdEncoding.EncodeToString([]byte(url))
	mobiledeCmd := exec.Command(filePath, encodedURL)

	output, err := mobiledeCmd.Output()
	if err != nil {
		return fmt.Errorf("error capturing output from 'mobilede': %w", err)
	}

	if err := os.WriteFile(file, output, 0644); err != nil {
		return fmt.Errorf("error writing output to file: %w", err)
	}

	return nil
}

func score(ctx context.Context, cmd *cli.Command) error {
	cars, err := getCarsFromFile(file)
	if err != nil {
		return fmt.Errorf("error getting cars from file: %w", err)
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
	return nil
}

func group(ctx context.Context, cmd *cli.Command) error {
	cars, err := getCarsFromFile(file)
	if err != nil {
		return fmt.Errorf("error getting cars from file: %w", err)
	}

	scores := analysis.ScoreCars(cars, 1.0, -1.0, -1.0, 0.0)
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

	table := tablewriter.NewWriter(os.Stdout)
	table.Header([]string{"Make", "Model", "Count", "Avg Age", "Avg Mileage", "Avg Price", "Avg Horsepower", "Fuel Type"})

	for _, g := range groups {
		table.Append([]string{
			g.Manufacturer,
			g.Model,
			fmt.Sprintf("%d", g.Amount),
			fmt.Sprintf("%.2f", g.AverageAge),
			fmt.Sprintf("%.0f km", g.AverageMileage),
			fmt.Sprintf("%.0f EUR", g.AveragePrice),
			fmt.Sprintf("%.0f hp", g.AverageHorsePower),
			g.FuelType,
		})
	}

	table.Render()
	return nil
}

func getCarsFromFile(path string) ([]common.Car, error) {
	content, err := readFile(file)
	if err != nil {
		return nil, fmt.Errorf("error reading file: %w", err)
	}

	cars, err := data.GetCarsFromMobileDeData(content)
	if err != nil {
		return nil, fmt.Errorf("error parsing car data: %w", err)
	}
	return cars, nil
}

func readFile(path string) ([]byte, error) {
	if _, err := os.Stat(path); os.IsNotExist(err) {
		return nil, fmt.Errorf("file does not exist: '%s'", path)
	}

	content, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("error reading file: %w", err)
	}

	return content, nil
}

func clickableLink(url, text string) string {
	return fmt.Sprintf("\033]8;;%s\033\\%s\033]8;;\033\\\n", url, text)
}
