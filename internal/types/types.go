package types

import "time"

type Car struct {
	ID                string
	KeyIdentifier     string
	ListingURL        string
	Price             float64
	Mileage           float64
	FirstRegistration time.Time
	Vehicle           *VehicleInfo
}

type VehicleInfo struct {
	KeyIdentifier      string
	Manufacturer       string
	Model              string
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
}

type VehicleInfoEntry struct {
	ID        string
	CreatedAt time.Time
	DataType  string
	Data      []byte
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
