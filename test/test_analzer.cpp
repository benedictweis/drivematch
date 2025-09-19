#include "analyzer.hpp"
#include "doctest.h"
#include "helper.hpp"

#include <iostream>

TEST_CASE("CarsAnalyzer Test") {
  std::vector<Car> cars;
  const int numCars = 100000;
  cars.reserve(numCars);
  for (int i = 0; i < numCars / 2; ++i) {
    cars.push_back(
        test::helper::generateRandomCarWithManufacturerAndModel("BMW", "X5"));
    cars.push_back(
        test::helper::generateRandomCarWithManufacturerAndModel("Audi", "A6"));
  }
  CarsAnalyzer analyzer(cars);

  SUBCASE("CarsAnalyzer::getScoredCars assigns a score to each car") {
    std::vector<ScoredCar> scoredCars = analyzer.getScoredCars();
    CHECK(!scoredCars.empty());
    CHECK(scoredCars.size() == numCars);
    for (const ScoredCar &scoredCar : scoredCars) {
      CHECK(scoredCar.score != 0.0f);
    }
  }

  SUBCASE("CarsAnalyzer::getScoredCars assigns a better score to a better car") {
    CarsAnalyzer analyzerWithTwoCars(
        {test::helper::WORSE_CAR, test::helper::BEST_CAR});

    std::vector<ScoredCar> scoredCars = analyzerWithTwoCars.getScoredCars();
    CHECK(!scoredCars.empty());
    CHECK(scoredCars.size() == 2);
    CHECK(scoredCars[0].score > scoredCars[1].score);
    CHECK(scoredCars[0].car.providerId == test::helper::BEST_CAR.providerId);
    CHECK(scoredCars[1].car.providerId == test::helper::WORSE_CAR.providerId);
  }
}
