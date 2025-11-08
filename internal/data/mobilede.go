package data

import (
	"encoding/json"
	"fmt"
	"strconv"
	"strings"
	"time"

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
		FuelType          string `json:"ft"`
	} `json:"attr"`
}

func GetCarsFromMobileDeData(data []byte) ([]common.Car, error) {
	mobileDeCars := make([]MobileDeCar, 0)
	err := json.Unmarshal(data, &mobileDeCars)
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
	var firstRegistration time.Time
	if strings.ToLower(mdc.Attr.FirstRegistration) == "neu" || mdc.Attr.FirstRegistration == "" {
		firstRegistration = time.Now()
	} else {
		var err error
		firstRegistration, err = time.Parse("01/2006", mdc.Attr.FirstRegistration)
		if err != nil {
			return common.Car{}, err
		}
	}

	mileageStr := strings.Map(func(r rune) rune {
		if r >= '0' && r <= '9' {
			return r
		}
		return -1
	}, mdc.Attr.Mileage)
	mileage, err := strconv.ParseFloat(mileageStr, 64)
	if err != nil {
		return common.Car{}, err
	}

	horsePowerParts := strings.Split(mdc.Attr.Power, "kW")
	horsePowerStr := strings.Map(func(r rune) rune {
		if r >= '0' && r <= '9' {
			return r
		}
		return -1
	}, horsePowerParts[1])
	horsePower, err := strconv.ParseFloat(horsePowerStr, 64)
	if err != nil {
		return common.Car{}, err
	}

	return common.Car{
		ID:                strconv.Itoa(mdc.ID),
		Manufacturer:      mdc.Manufacturer,
		Model:             mdc.Model,
		Price:             mdc.Price.GrossAmount,
		FirstRegistration: firstRegistration,
		Mileage:           mileage,
		HorsePower:        horsePower,
		FuelType:          mdc.Attr.FuelType,
		ListingURL:        fmt.Sprintf("https://suchen.mobile.de/fahrzeuge/details.html?id=%d", mdc.ID),
	}, nil
}
