package types

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
	VehicleInfo       *VehicleInfo
}

type VehicleInfo struct {
	ID                 string
	ProviderID         string
	CarHash            string
	KeyIdentifier      string
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

type UniqueCarGroup struct {
	Hash         string
	Amount       int
	Manufacturer string
	Model        string
	YearFrom     int
	YearTo       int
	HorsePower   float64
	FuelType     string
}

type Search struct {
	ID         string
	Name       string
	CreatedAt  time.Time
	SearchType string
	DataLen    int
}

type CarDetail struct {
	ID         string
	ProviderID string
	CarHash    string
	CreatedAt  time.Time
	DataType   string
	Data       []byte
}
