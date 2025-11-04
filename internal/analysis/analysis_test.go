package analysis

import (
	"math/rand"
	"testing"
	"time"

	"github.com/benedictweis/drivematch/internal/common"
)

const oneMillion = 1 * 1000 * 1000

func generateRandomCars(n int, manufacturer, model string) []common.Car {
	cars := make([]common.Car, n)
	for i := 0; i < n; i++ {
		cars[i] = common.Car{
			Manufacturer:      manufacturer,
			Model:             model,
			HorsePower:        rand.Float64()*(600-100) + 100,           // Random horsepower between 100 and 600
			Price:             rand.Float64()*(100000-5000) + 5000,      // Random price between 5,000 and 100,000
			Mileage:           rand.Float64() * 200000,                  // Random mileage between 0 and 200,000
			FirstRegistration: time.Now().AddDate(-rand.Intn(20), 0, 0), // Random age between 0 and 20 years
		}
	}
	return cars
}

func TestScoreCars(t *testing.T) {
	n := oneMillion
	cars := generateRandomCars(n, "Audi", "A6")
	_ = ScoreCars(cars, 1.0, -1.0, -1.0, -10)
}

func BenchmarkScoreCars(b *testing.B) {
	n := oneMillion
	cars := generateRandomCars(n, "Audi", "A6")
	for i := 0; i < b.N; i++ {
		_ = ScoreCars(cars, 1.0, -1.0, -1.0, -10)
	}
}

func TestGroupCars(t *testing.T) {
	n := oneMillion
	cars := append(
		generateRandomCars(n/2, "Audi", "A6"),
		generateRandomCars(n/2, "BMW", "X5")...,
	)
	rand.Shuffle(len(cars), func(i, j int) { cars[i], cars[j] = cars[j], cars[i] })
	scores := ScoreCars(cars, 1.0, -1.0, -1.0, -1.0)
	groups := GroupCars(cars, scores)
	if len(groups) != 2 {
		t.Errorf("expected 2 groups, got %d", len(groups))
	}
	if groups[0].Amount+groups[1].Amount != n {
		t.Errorf("expected total amount %d, got %d", n, groups[0].Amount+groups[1].Amount)
	}
}

func BenchmarkGroupCars(b *testing.B) {
	n := oneMillion
	cars := append(
		generateRandomCars(n/2, "Audi", "A6"),
		generateRandomCars(n/2, "BMW", "X5")...,
	)
	rand.Shuffle(len(cars), func(i, j int) { cars[i], cars[j] = cars[j], cars[i] })
	scores := ScoreCars(cars, 1.0, -1.0, -1.0, -1.0)
	for i := 0; i < b.N; i++ {
		_ = GroupCars(cars, scores)
	}
}
