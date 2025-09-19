#include "analyzer.hpp"
#include "doctest.h"
#include "helper.hpp"

#include <iostream>

TEST_CASE("CarsAnalyzer Test")
{
    SUBCASE("CarsAnalyzer::getScoredCars assigns a score to each car within time constraints")
    {
        std::vector<Car> cars;
        const int numCars = 100000;
        cars.reserve(numCars);
        for (int i = 0; i < numCars / 2; ++i)
        {
            cars.push_back(
                test::helper::generateRandomCarWithManufacturerAndModel("BMW", "X5"));
            cars.push_back(test::helper::generateRandomCarWithManufacturerAndModel(
                "Audi", "A6"));
        }
        CarsAnalyzer analyzerWithManyCars(cars);
        std::vector<ScoredCar> scoredCars = analyzerWithManyCars.getScoredCars();
        CHECK(scoredCars.size() == numCars);
        for (const ScoredCar &scoredCar : scoredCars)
        {
            CHECK(scoredCar.score != 0.0f);
        }
    }

    SUBCASE(
        "CarsAnalyzer::getScoredCars assigns a better score to a better car")
    {
        CarsAnalyzer analyzerWithTwoCars(
            {test::helper::WORSE_CAR, test::helper::BEST_CAR});

        std::vector<ScoredCar> scoredCars = analyzerWithTwoCars.getScoredCars();
        CHECK(scoredCars.size() == 2);
        CHECK(scoredCars[0].score > scoredCars[1].score);
        CHECK(scoredCars[0].car.providerId == test::helper::BEST_CAR.providerId);
        CHECK(scoredCars[1].car.providerId == test::helper::WORSE_CAR.providerId);
    }

    SUBCASE(
        "CarsAnalyzer::getScoredCars respects weights")
    {
        CarsAnalyzer analyzerWithTwoCars(
            {test::helper::WORSE_CAR, test::helper::BEST_CAR});

        analyzerWithTwoCars.setWeights(
            -1,
            1,
            1,
            1,
            100,
            1,
            100);

        std::vector<ScoredCar> scoredCars = analyzerWithTwoCars.getScoredCars();
        CHECK(scoredCars.size() == 2);
        CHECK(scoredCars[0].score > scoredCars[1].score);
        CHECK(scoredCars[0].car.providerId == test::helper::WORSE_CAR.providerId);
        CHECK(scoredCars[1].car.providerId == test::helper::BEST_CAR.providerId);
    }

    SUBCASE("CarsAnalyzer::getScoredCars respects filters")
    {
        const Car BMW_X5 = test::helper::generateRandomCarWithManufacturerAndModel("BMW", "X5");
        const Car BMW_M3 = test::helper::generateRandomCarWithManufacturerAndModel("BMW", "M3");
        const Car AUDI_A6 = test::helper::generateRandomCarWithManufacturerAndModel("Audi", "A6");
        const Car MERCEDES_E300 = test::helper::generateRandomCarWithManufacturerAndModel("Mercedes", "E300");

        CarsAnalyzer analyzerWithDifferentCars(
            {BMW_X5, BMW_M3, AUDI_A6, MERCEDES_E300});

        analyzerWithDifferentCars.setFilters({"BMW"}, {});
        std::vector<ScoredCar> scoredCars = analyzerWithDifferentCars.getScoredCars();
        CHECK(scoredCars.size() == 2);

        analyzerWithDifferentCars.setFilters({"BMW"}, {"X5"});
        scoredCars = analyzerWithDifferentCars.getScoredCars();
        CHECK(scoredCars.size() == 1);
        CHECK(scoredCars[0].car.providerId == BMW_X5.providerId);

        analyzerWithDifferentCars.setFilters({"BMW", "Audi"}, {"X5"});
        scoredCars = analyzerWithDifferentCars.getScoredCars();
        CHECK(scoredCars.size() == 1);
        CHECK(scoredCars[0].car.providerId == BMW_X5.providerId);

        analyzerWithDifferentCars.setFilters({"BMW", "Audi"}, {});
        scoredCars = analyzerWithDifferentCars.getScoredCars();
        CHECK(scoredCars.size() == 3);
    }
}
