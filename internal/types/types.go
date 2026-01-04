package types

import "time"

type Car struct {
	ID                string
	HSN               string
	TSN               string
	Manufacturer      string
	Model             string
	HorsePower        float64
	Price             float64
	Mileage           float64
	FirstRegistration time.Time
	FuelType          string
	ListingURL        string
	CarDetails        *CarDetails
}

type CarDetails struct {
	HSN                string
	TSN                string
	Manufacturer       string
	Model              string
	ProductionStart    time.Time
	ProductionEnd      time.Time
	Body               string
	HorsePower         float64
	Torque             float64
	FuelType           string
	Drivetrain         string
	TrunkVolume        int
	Acceleration0to100 float64
	TopSpeed           int
	NoiseLevel         float64
	FuelConsumption    string
	DetailsURL         string
}

type CarGroup struct {
	Amount         int
	HSN            string
	TSN            string
	Manufacturer   string
	Model          string
	HorsePower     float64
	AverageScore   float64
	AveragePrice   float64
	AverageMileage float64
	AverageAge     float64
	FuelType       string
	CarDetails     *CarDetails
}

type UniqueCarGroup struct {
	HSN string
	TSN string
}

type Search struct {
	ID         string
	Name       string
	CreatedAt  time.Time
	SearchType string
	DataLen    int
}

type CarDetail struct {
	ID        string
	HSN       string
	TSN       string
	CreatedAt time.Time
	DataType  string
	Data      []byte
}
