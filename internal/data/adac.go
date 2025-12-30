package data

import (
	"encoding/json"
	"fmt"
	"strconv"
	"strings"

	"github.com/benedictweis/drivematch/internal/database"
	"github.com/benedictweis/drivematch/internal/types"
)

const (
	HSNKey  = "HSN Schlüsselnummer"
	TSNKey  = "TSN Schlüsselnummer"
	TSN2Key = "TSN Schlüsselnummer 2"
)

func GetMissingKeyIdentifiers(db *database.SQLiteDatabase) ([]string, error) {
	allData, err := db.GetAllSearchData()
	if err != nil {
		return nil, fmt.Errorf("error getting all search data: %w", err)
	}

	setOfKeyIdentifiers := make(map[string]bool)
	for _, d := range allData {
		cars, err := GetCarsFromMobileDeData(d)
		if err != nil {
			return nil, fmt.Errorf("error parsing car data: %w", err)
		}
		for _, c := range cars {
			setOfKeyIdentifiers[c.KeyIdentifier] = true
		}
	}
	delete(setOfKeyIdentifiers, KeyIdentifierMissing)

	ids, err := db.GetAllVehicleInfoIds()
	if err != nil {
		return nil, fmt.Errorf("error getting all vehicle info IDs: %w", err)
	}

	for _, id := range ids {
		delete(setOfKeyIdentifiers, id)
	}

	var missingKeyIdentifiers []string
	for id := range setOfKeyIdentifiers {
		missingKeyIdentifiers = append(missingKeyIdentifiers, id)
	}

	return missingKeyIdentifiers, nil
}

type adacVehicleInfo struct {
	HSN               string `json:"HSN Schlüsselnummer"`
	TSN               string `json:"TSN Schlüsselnummer"`
	Make              string `json:"Marke"`
	Model             string `json:"Modell"`
	Body              string `json:"Karosserie"`
	HorsePower        string `json:"Leistung maximal in PS (Systemleistung)"`
	Torque            string `json:"Drehmoment (Systemleistung)"`
	FuelType          string `json:"Kraftstoffart"`
	Drivetrain        string `json:"Antriebsart"`
	TrunkVolume       string `json:"Kofferraumvolumen normal"`
	AccelerationTo100 string `json:"Beschleunigung 0-100km/h"`
	TopSpeed          string `json:"Höchstgeschwindigkeit"`
	NoiseLevel        string `json:"Fahrgeräusch"`
	FuelConsumption   string `json:"Verbrauch kombiniert (WLTP)"`
}

func GetVehicleInfoFromADACData(data []byte) (*types.VehicleInfo, error) {
	var avi adacVehicleInfo
	err := json.Unmarshal(data, &avi)
	if err != nil {
		return nil, fmt.Errorf("error unmarshaling ADAC vehicle info: %w", err)
	}

	torqueStr := strings.TrimSuffix(avi.Torque, " Nm")
	if torqueStr == "n.b." {
		torqueStr = "0"
	}
	torque, err := strconv.ParseFloat(torqueStr, 64)
	if err != nil {
		return nil, fmt.Errorf("error parsing torque value: %w", err)
	}

	accelerationTo100Str := strings.TrimSuffix(avi.AccelerationTo100, " s")
	accelerationTo100Str = strings.ReplaceAll(accelerationTo100Str, ",", ".")
	if accelerationTo100Str == "n.b." {
		accelerationTo100Str = "0"
	}
	accelerationTo100, err := strconv.ParseFloat(accelerationTo100Str, 64)
	if err != nil {
		return nil, fmt.Errorf("error parsing accelerationTo100 value: %w", err)
	}

	topSpeedStr := strings.TrimSuffix(avi.TopSpeed, " km/h")
	if topSpeedStr == "n.b." {
		topSpeedStr = "0"
	}
	topSpeed, err := strconv.Atoi(topSpeedStr)
	if err != nil {
		return nil, fmt.Errorf("error parsing topSpeed value: %w", err)
	}

	noiseLevelStr := strings.TrimSuffix(avi.NoiseLevel, " dB")
	noiseLevel, err := strconv.ParseFloat(noiseLevelStr, 64)
	if err != nil {
		return nil, fmt.Errorf("error parsing noiseLevel value: %w", err)
	}

	horsePower, err := strconv.ParseFloat(avi.HorsePower, 64)
	if err != nil {
		return nil, fmt.Errorf("error parsing horsePower value: %w", err)
	}

	trunkVolumeStr := strings.TrimSuffix(avi.TrunkVolume, " l")
	if trunkVolumeStr == "n.b." || trunkVolumeStr == "" {
		trunkVolumeStr = "0"
	}
	trunkVolume, err := strconv.Atoi(trunkVolumeStr)
	if err != nil {
		return nil, fmt.Errorf("error parsing trunkVolume value: %w", err)
	}

	vi := &types.VehicleInfo{
		KeyIdentifier:      fmt.Sprintf("%s/%s", avi.HSN, avi.TSN),
		Manufacturer:       avi.Make,
		Model:              avi.Model,
		Body:               avi.Body,
		HorsePower:         horsePower,
		Torque:             torque,
		FuelType:           avi.FuelType,
		Drivetrain:         avi.Drivetrain,
		TrunkVolume:        trunkVolume,
		Acceleration0to100: accelerationTo100,
		TopSpeed:           topSpeed,
		NoiseLevel:         noiseLevel,
		FuelConsumption:    avi.FuelConsumption,
	}

	return vi, nil
}
