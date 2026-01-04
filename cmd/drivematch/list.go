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
	listCarsSearchId string
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
			Flags: []cli.Flag{
				&cli.StringFlag{
					Name:        "search-id",
					Aliases:     []string{"sid"},
					Usage:       "filter cars to only those from the given search ID",
					Destination: &listCarsSearchId,
				},
			},
		},
		{
			Name:   "cars-no-adac",
			Usage:  "list unique cars identified across all searches that do not have ADAC details scraped yet",
			Action: listCarsNoADAC,
			Flags: []cli.Flag{
				&cli.StringFlag{
					Name:        "search-id",
					Aliases:     []string{"sid"},
					Usage:       "filter cars to only those from the given search ID",
					Destination: &listCarsSearchId,
				},
			},
		},
		{
			Name:   "car-details",
			Usage:  "list scraped car details entries from adac",
			Action: listCarDetails,
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
	cars := make([]types.Car, 0)

	if listCarsSearchId != "" {
		searchData, err := db.GetSearchData(listCarsSearchId)
		if err != nil {
			return fmt.Errorf("error getting search data from database: %w", err)
		}

		cars, err = scraping.GetCarsFromMobileDeData(searchData)
		if err != nil {
			return fmt.Errorf("error parsing car data: %w", err)
		}
	} else {
		searches, err := db.GetAllSearchData()
		if err != nil {
			return fmt.Errorf("error getting searches from database: %w", err)
		}

		for _, searchData := range searches {
			searchCars, err := scraping.GetCarsFromMobileDeData(searchData)
			if err != nil {
				return fmt.Errorf("error parsing car data: %w", err)
			}
			cars = append(cars, searchCars...)
		}
	}

	uniqueCars := analysis.GetUniqueCars(cars)

	sort.Slice(uniqueCars, func(i, j int) bool {
		if uniqueCars[i].HSN != uniqueCars[j].HSN {
			return uniqueCars[i].HSN < uniqueCars[j].HSN
		}
		return uniqueCars[i].TSN < uniqueCars[j].TSN
	})

	columns := 2
	table := make([]string, (len(uniqueCars)+1)*columns)

	table[0] = "HSN"
	table[1] = "TSN"

	for i, g := range uniqueCars {
		baseIdx := (i + 1) * columns
		table[baseIdx+0] = g.HSN
		table[baseIdx+1] = g.TSN
	}

	outputWriter.WriteTable(columns, table)
	return nil
}

func listCarsNoADAC(ctx context.Context, cmd *cli.Command) error {
	cars := make([]types.Car, 0)

	if listCarsSearchId != "" {
		searchData, err := db.GetSearchData(listCarsSearchId)
		if err != nil {
			return fmt.Errorf("error getting search data from database: %w", err)
		}

		cars, err = scraping.GetCarsFromMobileDeData(searchData)
		if err != nil {
			return fmt.Errorf("error parsing car data: %w", err)
		}
	} else {
		searches, err := db.GetAllSearchData()
		if err != nil {
			return fmt.Errorf("error getting searches from database: %w", err)
		}

		for _, searchData := range searches {
			searchCars, err := scraping.GetCarsFromMobileDeData(searchData)
			if err != nil {
				return fmt.Errorf("error parsing car data: %w", err)
			}
			cars = append(cars, searchCars...)
		}
	}

	uniqueCars := analysis.GetUniqueCars(cars)

	carDetailsData, err := db.GetAllCarDetails()
	if err != nil {
		return fmt.Errorf("error getting car details from database: %w", err)
	}

	carDetailsMap := make(map[types.UniqueCarGroup]bool)
	for _, cd := range carDetailsData {
		carDetails, err := scraping.GetCarDetailsFromADACData(cd.Data)
		if err != nil {
			return fmt.Errorf("error parsing car detail data: %w", err)
		}

		uc := types.UniqueCarGroup{
			HSN: carDetails.HSN,
			TSN: carDetails.TSN,
		}

		carDetailsMap[uc] = true
	}

	uniqueCarsNoADAC := make([]types.UniqueCarGroup, 0)

	for _, uc := range uniqueCars {
		_, exists := carDetailsMap[uc]
		if !exists {
			uniqueCarsNoADAC = append(uniqueCarsNoADAC, uc)
		}
	}

	sort.Slice(uniqueCarsNoADAC, func(i, j int) bool {
		if uniqueCarsNoADAC[i].HSN != uniqueCarsNoADAC[j].HSN {
			return uniqueCarsNoADAC[i].HSN < uniqueCarsNoADAC[j].HSN
		}
		return uniqueCarsNoADAC[i].TSN < uniqueCarsNoADAC[j].TSN
	})

	columns := 2
	table := make([]string, (len(uniqueCarsNoADAC)+1)*columns)

	table[0] = "HSN"
	table[1] = "TSN"

	for i, g := range uniqueCarsNoADAC {
		baseIdx := (i + 1) * columns
		table[baseIdx+0] = g.HSN
		table[baseIdx+1] = g.TSN
	}

	outputWriter.WriteTable(columns, table)
	return nil
}

func listCarDetails(ctx context.Context, cmd *cli.Command) error {
	carDetails, err := db.GetAllCarDetails()
	if err != nil {
		return fmt.Errorf("error getting car details from database: %w", err)
	}

	columns := 6
	table := make([]string, (len(carDetails)+1)*columns)

	table[0] = "ID"
	table[1] = "HSN"
	table[2] = "TSN"
	table[3] = "Created At"
	table[4] = "Data Type"
	table[5] = "Data Length"

	for i, cd := range carDetails {
		baseIdx := (i + 1) * columns
		table[baseIdx+0] = cd.ID
		table[baseIdx+1] = cd.HSN
		table[baseIdx+2] = cd.TSN
		table[baseIdx+3] = cd.CreatedAt.Format("2006-01-02 15:04:05")
		table[baseIdx+4] = cd.DataType
		table[baseIdx+5] = output.DataLength(len(cd.Data))
	}

	outputWriter.WriteTable(columns, table)
	return nil
}
