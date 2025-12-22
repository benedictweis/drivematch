package main

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/benedictweis/drivematch/internal/database"
	"github.com/urfave/cli/v3"
)

var getCmd *cli.Command = &cli.Command{
	Name:      "get",
	Usage:     "get raw contents of a search",
	UsageText: "drivematch get <searchId>",
	Arguments: []cli.Argument{
		&cli.StringArg{
			Name:        "searchId",
			Destination: &searchId,
			UsageText:   "the ID of the search to get raw contents from",
		},
	},
	Action: get,
}

func get(ctx context.Context, cmd *cli.Command) error {
	if searchId == "" {
		fmt.Println("searchId must be provided")
		return cli.ShowSubcommandHelp(cmd)
	}

	db := database.NewSQLiteDatabase(databasePath)

	if err := db.Connect(); err != nil {
		return fmt.Errorf("error connecting to database: %w", err)
	}
	defer db.Close()

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

	fmt.Println(string(prettyJSON))

	return nil
}
