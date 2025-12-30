package data

import (
	"github.com/benedictweis/drivematch/internal/types"
)

func AttachVehicleInfosToCars(cars []types.Car, vehicleInfos map[string]*types.VehicleInfo) ([]types.Car, int, error) {
	newCars := make([]types.Car, 0, len(cars))
	failedToMap := 0

	for _, car := range cars {
		if vi, ok := vehicleInfos[car.KeyIdentifier]; ok {
			car.Vehicle = vi
			newCars = append(newCars, car)
		} else {
			failedToMap++
		}
	}
	return newCars, failedToMap, nil
}
