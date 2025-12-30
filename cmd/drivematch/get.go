package main

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/benedictweis/drivematch/internal/scraping"
	"github.com/urfave/cli/v3"
)

var (
	dataType string
	objectId string
)

var getCmd *cli.Command = &cli.Command{
	Name:      "get",
	Usage:     "get raw contents of a search",
	UsageText: "drivematch get <type> <Id>",
	Arguments: []cli.Argument{
		&cli.StringArg{
			Name:        "type",
			Destination: &dataType,
			UsageText:   "the type of data to get (listing or cars)",
		},
		&cli.StringArg{
			Name:        "Id",
			Destination: &objectId,
			UsageText:   "the ID of the object to get",
		},
	},
	Action: get,
}

func get(ctx context.Context, cmd *cli.Command) error {
	if dataType != "listing" && dataType != "cars" {
		fmt.Println("Invalid type. Must be 'listings', 'cars', or 'vehicle_info'.")
		return cli.ShowSubcommandHelp(cmd)
	}
	if objectId == "" {
		fmt.Println("Id must be provided")
		return cli.ShowSubcommandHelp(cmd)
	}

	var output string

	switch dataType {
	case "listing":
		searchData, err := db.GetSearchData(objectId)
		if err != nil {
			return fmt.Errorf("error getting searches from database: %w", err)
		}

		var jsonData any
		if err := json.Unmarshal(searchData, &jsonData); err != nil {
			return fmt.Errorf("error parsing search data as JSON: %w", err)
		}

		prettyJSON, err := json.MarshalIndent(jsonData, "", "  ")
		if err != nil {
			return fmt.Errorf("error formatting JSON: %w", err)
		}
		output = string(prettyJSON)
	case "cars":
		searchData, err := db.GetSearchData(objectId)
		if err != nil {
			return fmt.Errorf("error getting searches from database: %w", err)
		}

		cars, err := scraping.GetCarsFromMobileDeData(searchData)
		if err != nil {
			return fmt.Errorf("error parsing car data: %w", err)
		}

		prettyJSON, err := json.MarshalIndent(cars, "", "  ")
		if err != nil {
			return fmt.Errorf("error formatting JSON: %w", err)
		}
		output = string(prettyJSON)
	}
	fmt.Println(output)

	return nil
}
