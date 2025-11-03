package data

import (
	"encoding/json"
	"strconv"

	"github.com/benedictweis/drivematch/internal/common"
)

type MobileDeCar struct {
	ID           int    `json:"id"`
	Manufacturer string `json:"make"`
	Model        string `json:"model"`
	Price        struct {
		GrossAmount float64 `json:"grossAmount"`
	} `json:"price"`
	Attr struct {
		Power             string `json:"pw"`
		Mileage           string `json:"ml"`
		FirstRegistration string `json:"fr"`
	} `json:"attr"`
}

func GetCarsFromMobileDeData(data string) ([]common.Car, error) {
	mobileDeCars := make([]MobileDeCar, 0)
	err := json.Unmarshal([]byte(data), &mobileDeCars)
	if err != nil {
		return nil, err
	}

	cars := make([]common.Car, 0, len(mobileDeCars))
	for _, mdc := range mobileDeCars {
		car, err := convertMobileDeCarToCommonCar(mdc)
		if err != nil {
			return nil, err
		}
		cars = append(cars, car)
	}
	return cars, nil
}

func convertMobileDeCarToCommonCar(mdc MobileDeCar) (common.Car, error) {
	return common.Car{
		ID:           strconv.Itoa(mdc.ID),
		Manufacturer: mdc.Manufacturer,
		Model:        mdc.Model,
		Price:        mdc.Price.GrossAmount,
	}, nil
}
