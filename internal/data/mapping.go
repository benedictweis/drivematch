package data

import "github.com/benedictweis/drivematch/internal/common"

func AttachVehicleInfosToCars(cars []common.Car, vehicleInfos map[string]*common.VehicleInfo) ([]common.Car, int, error) {
	newCars := make([]common.Car, 0, len(cars))
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
