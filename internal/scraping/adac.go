package scraping

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"os/exec"
	"strconv"
	"strings"

	"github.com/benedictweis/drivematch/internal/types"
)

func ScrapeADAC(keywords []string) ([]byte, error) {
	err := extractPythonBundle()
	if err != nil {
		return nil, fmt.Errorf("error extracting python bundle: %w", err)
	}

	encodedKeywords, err := json.Marshal(keywords)
	if err != nil {
		return nil, fmt.Errorf("error marshaling keywords to JSON: %w", err)
	}
	encodedKeyIdentifiers := base64.StdEncoding.EncodeToString(encodedKeywords)

	fmt.Println("Attention: You will need to solve a google captcha once the Firefox browser opens!")
	adacCmd := exec.Command(scrapingBinaryPath(), "adac", encodedKeyIdentifiers)

	output, err := adacCmd.Output()
	if err != nil {
		return nil, fmt.Errorf("error capturing output from 'adac': %w", err)
	}

	return output, nil
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
