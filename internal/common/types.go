package common

import "time"

type Car struct {
	ID                string
	Manufacturer      string
	Model             string
	HorsePower        float64
	Price             float64
	Mileage           float64
	FirstRegistration time.Time
	FuelType          string
	ListingURL        string
}

type CarGroup struct {
	Amount            int
	Manufacturer      string
	Model             string
	AverageScore      float64
	AverageHorsePower float64
	AveragePrice      float64
	AverageMileage    float64
	AverageAge        float64
	FuelType          string
}

type Search struct {
	ID         string
	Name       string
	CreatedAt  time.Time
	SearchType string
	DataLen    int
}
