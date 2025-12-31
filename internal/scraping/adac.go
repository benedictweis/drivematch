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

type ADACScrapeTarget struct {
	CarHash string            `json:"car_hash"`
	URL     string            `json:"url"`
	Data    map[string]string `json:"data,omitempty"`
}

func ParseADACScrapeFile(content []byte) ([]ADACScrapeTarget, error) {
	var targets []ADACScrapeTarget

	lines := strings.Split(string(content), "\n")
	if len(lines) == 0 {
		return targets, nil
	}

	// Skip header
	for i := 1; i < len(lines); i++ {
		line := strings.TrimSpace(lines[i])
		if line == "" {
			continue
		}

		parts := strings.Split(line, ";")
		if len(parts) < 2 {
			continue
		}

		carHash := strings.TrimSpace(parts[0])

		// Check all parts from the end for ADAC URLs
		for j := len(parts) - 1; j >= 1; j-- {
			url := strings.TrimSpace(parts[j])
			if strings.HasPrefix(url, "https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle") {
				targets = append(targets, ADACScrapeTarget{
					CarHash: carHash,
					URL:     url,
				})
			}
		}
	}

	return targets, nil
}

func ScrapeADAC(targets []ADACScrapeTarget) ([]ADACScrapeTarget, error) {
	err := extractPythonBundle()
	if err != nil {
		return nil, fmt.Errorf("error extracting python bundle: %w", err)
	}

	targetsJson, err := json.Marshal(targets)
	if err != nil {
		return nil, fmt.Errorf("error marshaling targets to JSON: %w", err)
	}
	encodedTargets := base64.StdEncoding.EncodeToString(targetsJson)

	adacCmd := exec.Command(scrapingBinaryPath(), "adac", encodedTargets)

	output, err := adacCmd.Output()
	if err != nil {
		return nil, fmt.Errorf("error capturing output from 'adac': %w", err)
	}

	var result []ADACScrapeTarget
	err = json.Unmarshal(output, &result)
	if err != nil {
		return nil, fmt.Errorf("error unmarshaling output from 'adac': %w", err)
	}

	return result, nil
}

type adacVehicleInfo struct {
	HSN               string `json:"HSN Schlüsselnummer"`
	TSN               string `json:"TSN Schlüsselnummer"`
	Make              string `json:"Marke"`
	Model             string `json:"Modell"`
	ProductionStart   string `json:"Baureihenstart"`
	ProductionEnd     string `json:"Baureihenende"`
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

func GetVehicleInfoFromADACData(carDetail *types.CarDetail) (*types.VehicleInfo, error) {
	var avi adacVehicleInfo
	err := json.Unmarshal(carDetail.Data, &avi)
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

	var productionStart, productionEnd time.Time

	if avi.ProductionStart != "" && avi.ProductionStart != "n.b." {
		if t, err := time.Parse("01/06", avi.ProductionStart); err == nil {
			productionStart = t
		} else if t, err := time.Parse("01/2006", avi.ProductionStart); err == nil {
			productionStart = t
		}
	}

	if avi.ProductionEnd != "" && avi.ProductionEnd != "n.b." {
		if t, err := time.Parse("01/06", avi.ProductionEnd); err == nil {
			productionEnd = t
		} else if t, err := time.Parse("01/2006", avi.ProductionEnd); err == nil {
			productionEnd = t
		}
	}

	vi := &types.VehicleInfo{
		ID:                 carDetail.ID,
		ProviderID:         carDetail.ProviderID,
		CarHash:            carDetail.CarHash,
		KeyIdentifier:      fmt.Sprintf("%s/%s", avi.HSN, avi.TSN),
		Manufacturer:       avi.Make,
		Model:              avi.Model,
		ProductionStart:    productionStart,
		ProductionEnd:      productionEnd,
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
