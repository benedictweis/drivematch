package data

import (
	"encoding/json"
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/benedictweis/drivematch/internal/types"
)

const (
	MobileDeSearchType   = "mobilede"
	KeyIdentifierMissing = "unknown"
)

type mobileDeListingInfo struct {
	ID    int `json:"id"`
	Price struct {
		GrossAmount float64 `json:"grossAmount"`
	} `json:"price"`
	Attr struct {
		Mileage           string `json:"ml"`
		FirstRegistration string `json:"fr"`
	} `json:"attr"`
	KBA struct {
		HSN string `json:"hsn"`
		TSN string `json:"tsn"`
	} `json:"kba"`
}

func GetCarsFromMobileDeData(data []byte) ([]types.Car, error) {
	mobileDeCars := make([]mobileDeListingInfo, 0)
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

func convertMobileDeCarToCommonCar(mdc mobileDeListingInfo) (types.Car, error) {
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

	var keyIdentifier string
	if mdc.KBA.HSN != "" || mdc.KBA.TSN != "" {
		keyIdentifier = fmt.Sprintf("%s/%s", mdc.KBA.HSN, mdc.KBA.TSN)
	} else {
		keyIdentifier = KeyIdentifierMissing
	}

	return types.Car{
		ID:                strconv.Itoa(mdc.ID),
		KeyIdentifier:     keyIdentifier,
		ListingURL:        fmt.Sprintf("https://suchen.mobile.de/fahrzeuge/details.html?id=%d", mdc.ID),
		Price:             mdc.Price.GrossAmount,
		Mileage:           mileage,
		FirstRegistration: firstRegistration,
	}, nil
}
