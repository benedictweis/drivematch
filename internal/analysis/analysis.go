package analysis

import (
	"crypto/sha256"
	"fmt"
	"math"
	"strings"
	"time"

	"github.com/benedictweis/drivematch/internal/types"
)

func ScoreCars(cars []types.Car, weightHorsePower, weightPrice, weightMileage, weightAge float64) []float64 {
	n := len(cars)
	if n == 0 {
		return nil
	}

	now := time.Now()
	ages := make([]float64, n)

	for i, c := range cars {
		ages[i] = now.Sub(c.FirstRegistration).Hours() / 24 // age in days
	}

	minHP, maxHP := math.MaxFloat64, -math.MaxFloat64
	minPrice, maxPrice := math.MaxFloat64, -math.MaxFloat64
	minMileage, maxMileage := math.MaxFloat64, -math.MaxFloat64
	minAge, maxAge := math.MaxFloat64, -math.MaxFloat64

	for i, c := range cars {
		hp := c.HorsePower
		price := c.Price
		mileage := c.Mileage
		age := ages[i]
		if hp < minHP {
			minHP = hp
		}
		if hp > maxHP {
			maxHP = hp
		}
		if price < minPrice {
			minPrice = price
		}
		if price > maxPrice {
			maxPrice = price
		}
		if mileage < minMileage {
			minMileage = mileage
		}
		if mileage > maxMileage {
			maxMileage = mileage
		}
		if age < minAge {
			minAge = age
		}
		if age > maxAge {
			maxAge = age
		}
	}

	horsePowerDenom := maxHP - minHP
	priceDenom := maxPrice - minPrice
	mileageDenom := maxMileage - minMileage
	ageDenom := maxAge - minAge

	scores := make([]float64, n)

	for i, c := range cars {
		horsePower := (c.HorsePower - minHP) / horsePowerDenom
		price := (c.Price - minPrice) / priceDenom
		mileage := (c.Mileage - minMileage) / mileageDenom
		age := (ages[i] - minAge) / ageDenom
		scores[i] = (weightHorsePower * horsePower) + (weightPrice * price) + (weightMileage * mileage) + (weightAge * age)
	}

	return scores
}

func GroupCars(cars []types.Car, scores []float64) []types.CarGroup {
	type groupKey struct{ manufacturer, model string }

	now := time.Now()
	groups := make(map[groupKey]*types.CarGroup)

	for i, c := range cars {
		key := groupKey{c.Manufacturer, c.Model}

		g, exists := groups[key]
		if !exists {
			g = &types.CarGroup{
				Manufacturer: c.Manufacturer,
				Model:        c.Model,
			}
			groups[key] = g
		}

		age := now.Sub(c.FirstRegistration).Hours() / 24 // age in days

		g.Amount++
		g.AverageScore += scores[i]
		g.AverageHorsePower += c.HorsePower
		g.AveragePrice += c.Price
		g.AverageMileage += c.Mileage
		g.AverageAge += age

		if g.FuelType == "" {
			g.FuelType = c.FuelType
		} else if g.FuelType != c.FuelType {
			g.FuelType = "Mixed"
		}
	}

	result := make([]types.CarGroup, 0, len(groups))
	for _, g := range groups {
		n := float64(g.Amount)
		g.AverageScore /= n
		g.AverageHorsePower /= n
		g.AveragePrice /= n
		g.AverageMileage /= n
		g.AverageAge /= n
		result = append(result, *g)
	}

	return result
}

func GetUniqueCars(cars []types.Car) []types.UniqueCarGroup {
	uniqueCars := make(map[string]*types.UniqueCarGroup)
	for _, c := range cars {
		hash := HashCar(&c)
		uc, exists := uniqueCars[hash]
		if !exists {
			uc = &types.UniqueCarGroup{
				Hash:         hash,
				Manufacturer: c.Manufacturer,
				Model:        c.Model,
				HorsePower:   c.HorsePower,
				FuelType:     c.FuelType,
			}
			uniqueCars[hash] = uc
		}
		uc.Amount++
		year := c.FirstRegistration.Year()
		if uc.YearFrom == 0 || year < uc.YearFrom {
			uc.YearFrom = year
		}
		if year > uc.YearTo {
			uc.YearTo = year
		}
	}

	result := make([]types.UniqueCarGroup, 0, len(uniqueCars))
	for _, uc := range uniqueCars {
		result = append(result, *uc)
	}

	return result
}

func HashCar(c *types.Car) string {
	data := fmt.Sprintf("%s|%s|%.2f|%s",
		strings.ToLower(c.Manufacturer),
		strings.ToLower(c.Model),
		c.HorsePower,
		strings.ToLower(c.FuelType))
	hash := sha256.Sum256([]byte(data))
	return fmt.Sprintf("%x", hash)
}

func MapCarToVehicleInfo(car *types.Car, vehicleInfos map[string][]*types.VehicleInfo) bool {
	vi, exists := vehicleInfos[HashCar(car)]
	if !exists {
		return false
	} else {
		for _, info := range vi {
			if car.FirstRegistration.Year() <= info.ProductionStart.Year() || car.FirstRegistration.Year() >= info.ProductionEnd.Year() {
				car.VehicleInfo = info
				return true
			}
		}
	}
	return false
}
