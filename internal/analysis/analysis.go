package analysis

import (
	"math"
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

func GroupCars(cars []types.Car, scores []float64, carDetails map[types.UniqueCarGroup]*types.CarDetails) []types.CarGroup {
	now := time.Now()
	groups := make(map[types.UniqueCarGroup]*types.CarGroup)

	for i, c := range cars {
		key := types.UniqueCarGroup{HSN: c.HSN, TSN: c.TSN}

		if key.HSN == "" || key.TSN == "" {
			continue
		}

		g, exists := groups[key]
		if !exists {
			g = &types.CarGroup{
				HSN:          c.HSN,
				TSN:          c.TSN,
				Manufacturer: c.Manufacturer,
				Model:        c.Model,
				HorsePower:   c.HorsePower,
				FuelType:     c.FuelType,
			}
			MapCarGroupToCarDetails(g, carDetails)
			groups[key] = g
		}

		age := now.Sub(c.FirstRegistration).Hours() / 24 // age in days

		g.Amount++
		g.AverageScore += scores[i]
		g.AveragePrice += c.Price
		g.AverageMileage += c.Mileage
		g.AverageAge += age
	}

	result := make([]types.CarGroup, 0, len(groups))
	for _, g := range groups {
		n := float64(g.Amount)
		g.AverageScore /= n
		g.AveragePrice /= n
		g.AverageMileage /= n
		g.AverageAge /= n
		result = append(result, *g)
	}

	return result
}

func GetUniqueCars(cars []types.Car) []types.UniqueCarGroup {
	uniqueCars := make(map[types.UniqueCarGroup]bool)
	for _, c := range cars {
		if c.HSN == "" || c.TSN == "" {
			continue
		}

		uc := types.UniqueCarGroup{
			HSN: c.HSN,
			TSN: c.TSN,
		}
		uniqueCars[uc] = true
	}

	result := make([]types.UniqueCarGroup, 0, len(uniqueCars))
	for uc := range uniqueCars {
		result = append(result, uc)
	}

	return result
}

func MapCarToCarDetails(car *types.Car, carDetails map[types.UniqueCarGroup]*types.CarDetails) bool {
	uc := types.UniqueCarGroup{
		HSN: car.HSN,
		TSN: car.TSN,
	}

	cd, exists := carDetails[uc]
	if !exists {
		return false
	} else {
		car.CarDetails = cd
	}
	return false
}

func MapCarGroupToCarDetails(cg *types.CarGroup, carDetails map[types.UniqueCarGroup]*types.CarDetails) bool {
	uc := types.UniqueCarGroup{
		HSN: cg.HSN,
		TSN: cg.TSN,
	}

	cd, exists := carDetails[uc]
	if !exists {
		return false
	} else {
		cg.CarDetails = cd
	}
	return false
}
