package scraping

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"os/exec"
	"strconv"
	"strings"
	"time"

	"github.com/benedictweis/drivematch/internal/types"
)

func ScrapeMobileDe(url string) ([]byte, error) {
	err := extractPythonBundle()
	if err != nil {
		return nil, fmt.Errorf("error extracting python bundle: %w", err)
	}

	encodedURL := base64.StdEncoding.EncodeToString([]byte(url))
	mobiledeCmd := exec.Command(scrapingBinaryPath(), "mobilede", encodedURL)

	output, err := mobiledeCmd.Output()
	if err != nil {
		return nil, fmt.Errorf("error capturing output from 'mobilede': %w", err)
	}

	return output, nil
}

const MobileDeSearchType = "mobilede"

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

func GetCarsFromMobileDeData(data []byte) ([]types.Car, error) {
	mobileDeCars := make([]MobileDeCar, 0)
	err := json.Unmarshal(data, &mobileDeCars)
	if err != nil {
		return nil, err
	}

	cars := make([]types.Car, 0, len(mobileDeCars))
	for _, mdc := range mobileDeCars {
		car, err := convertMobileDeCarToCommonCar(mdc)
		if err != nil {
			return nil, err
		}
		cars = append(cars, car)
	}
	return cars, nil
}

func convertMobileDeCarToCommonCar(mdc MobileDeCar) (types.Car, error) {
	var firstRegistration time.Time
	if strings.ToLower(mdc.Attr.FirstRegistration) == "neu" || mdc.Attr.FirstRegistration == "" {
		firstRegistration = time.Now()
	} else {
		var err error
		firstRegistration, err = time.Parse("01/2006", mdc.Attr.FirstRegistration)
		if err != nil {
			return types.Car{}, err
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
		return types.Car{}, err
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
		return types.Car{}, err
	}

	return types.Car{
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
