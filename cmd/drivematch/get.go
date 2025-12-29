package main

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/benedictweis/drivematch/internal/data"
	"github.com/benedictweis/drivematch/internal/database"
	"github.com/urfave/cli/v3"
)

var dataType string

var getCmd *cli.Command = &cli.Command{
	Name:      "get",
	Usage:     "get raw contents of a search",
	UsageText: "drivematch get <type> <searchId>",
	Arguments: []cli.Argument{
		&cli.StringArg{
			Name:        "type",
			Destination: &dataType,
			UsageText:   "the type of data to get (raw or cars)",
		},
		&cli.StringArg{
			Name:        "searchId",
			Destination: &searchId,
			UsageText:   "the ID of the search to get raw contents from",
		},
	},
	Action: get,
}

func get(ctx context.Context, cmd *cli.Command) error {
	if dataType != "listings" && dataType != "cars" && dataType != "vehicle_info" {
		fmt.Println("Invalid type. Must be 'listings', 'cars', or 'vehicle_info'.")
		return cli.ShowSubcommandHelp(cmd)
	}
	if searchId == "" {
		fmt.Println("searchId must be provided")
		return cli.ShowSubcommandHelp(cmd)
	}

	db := database.NewSQLiteDatabase(databasePath)

	if err := db.Connect(); err != nil {
		return fmt.Errorf("error connecting to database: %w", err)
	}
	defer db.Close()

	var output string

	switch dataType {
	case "listings":
		searchData, err := db.GetSearchData(searchId)
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
		searchData, err := db.GetSearchData(searchId)
		if err != nil {
			return fmt.Errorf("error getting searches from database: %w", err)
		}

		cars, err := data.GetCarsFromMobileDeData(searchData)
		if err != nil {
			return fmt.Errorf("error parsing car data: %w", err)
		}

		prettyJSON, err := json.MarshalIndent(cars, "", "  ")
		if err != nil {
			return fmt.Errorf("error formatting JSON: %w", err)
		}
		output = string(prettyJSON)
	case "vehicle_info":
		vehicleInfos, err := db.GetVehicleInfo(searchId)
		if err != nil {
			return fmt.Errorf("error getting vehicle info: %w", err)
		}

		var jsonData any
		if err := json.Unmarshal(vehicleInfos, &jsonData); err != nil {
			return fmt.Errorf("error parsing search data as JSON: %w", err)
		}

		prettyJSON, err := json.MarshalIndent(jsonData, "", "  ")
		if err != nil {
			return fmt.Errorf("error formatting JSON: %w", err)
		}
		output = string(prettyJSON)
	}

	fmt.Println(output)

	return nil
}
