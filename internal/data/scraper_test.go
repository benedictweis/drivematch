package data

import "testing"

func TestGetCarsFromURL(t *testing.T) {
	t.Run("it should return cars from a mobile.de URL", func(t *testing.T) {
		url := "https://suchen.mobile.de/fahrzeuge/search.html?dam=false&isSearchRequest=true&ms=3500%3B87%3B%3B&ref=quickSearch&s=Car&vc=Car"
		cars, err := GetCarsFromURL(url)
		if err != nil {
			t.Fatalf("expected no error, got %v", err)
		}
		if len(cars) == 0 {
			t.Fatalf("expected some cars, got none")
		}
	})
}
