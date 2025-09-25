#include "analyzer.hpp"
#include "doctest/doctest.h"
#include "helper.hpp"

TEST_SUITE("CarsAnalyzer Test Suite") {
    const Car BMW_X5 =
        test::helper::generateRandomCarWithManufacturerAndModel("BMW", "X5");
    const Car BMW_M3 =
        test::helper::generateRandomCarWithManufacturerAndModel("BMW", "M3");
    const Car AUDI_A6 =
        test::helper::generateRandomCarWithManufacturerAndModel("Audi", "A6");
    const Car MERCEDES_E300 =
        test::helper::generateRandomCarWithManufacturerAndModel("Mercedes",
                                                                "E300");

    TEST_CASE_FIXTURE(test::helper::ManyCarsFixture,
                      "CarsAnalyzer::getScoredCars assigns a score to each car "
                      "within time constraints [unit][performance]" *
                          doctest::timeout(1)) {
        CarsAnalyzer analyzerWithManyCars(getManyCars());
        std::vector<ScoredCar> scoredCars =
            analyzerWithManyCars.getScoredCars();
        CHECK(scoredCars.size() == getNumCars());
        for (const ScoredCar &scoredCar : scoredCars) {
            CHECK(scoredCar.score != 0.0f);
        }
    }

    TEST_CASE(
        "CarsAnalyzer::getScoredCars assigns a better score to a better car [unit]") {
        CarsAnalyzer analyzerWithTwoCars(
            {test::helper::WORST_CAR, test::helper::BEST_CAR});

        std::vector<ScoredCar> scoredCars = analyzerWithTwoCars.getScoredCars();
        CHECK(scoredCars.size() == 2);
        CHECK(scoredCars[0].score > scoredCars[1].score);
        CHECK(scoredCars[0].car.providerId ==
              test::helper::BEST_CAR.providerId);
        CHECK(scoredCars[1].car.providerId ==
              test::helper::WORST_CAR.providerId);
    }

    TEST_CASE("CarsAnalyzer::getScoredCars respects weights [unit]") {
        CarsAnalyzer analyzerWithTwoCars(
            {test::helper::WORST_CAR, test::helper::BEST_CAR});

        analyzerWithTwoCars.setWeights({-1, 1, 1, 1, 100, 1, 100});

        std::vector<ScoredCar> scoredCars = analyzerWithTwoCars.getScoredCars();
        CHECK(scoredCars.size() == 2);
        CHECK(scoredCars[0].score > scoredCars[1].score);
        CHECK(scoredCars[0].car.providerId ==
              test::helper::WORST_CAR.providerId);
        CHECK(scoredCars[1].car.providerId ==
              test::helper::BEST_CAR.providerId);
    }

    TEST_CASE("CarsAnalyzer::getScoredCars respects filters [unit]") {
        CarsAnalyzer analyzerWithDifferentCars(
            {BMW_X5, BMW_M3, AUDI_A6, MERCEDES_E300});

        analyzerWithDifferentCars.setFilters({{"BMW"}, {}});
        std::vector<ScoredCar> scoredCars =
            analyzerWithDifferentCars.getScoredCars();
        CHECK(scoredCars.size() == 2);

        analyzerWithDifferentCars.setFilters({{"BMW"}, {"X5"}});
        scoredCars = analyzerWithDifferentCars.getScoredCars();
        CHECK(scoredCars.size() == 1);
        CHECK(scoredCars[0].car.providerId == BMW_X5.providerId);

        analyzerWithDifferentCars.setFilters({{"BMW", "Audi"}, {"X5"}});
        scoredCars = analyzerWithDifferentCars.getScoredCars();
        CHECK(scoredCars.size() == 1);
        CHECK(scoredCars[0].car.providerId == BMW_X5.providerId);

        analyzerWithDifferentCars.setFilters({{"BMW", "Audi"}, {}});
        scoredCars = analyzerWithDifferentCars.getScoredCars();
        CHECK(scoredCars.size() == 3);
    }

    TEST_CASE(
        "CarsAnalyzer::getGroupedCarsByManufacturerAndModel groups cars by "
        "manufacturer and model [unit]") {
        CarsAnalyzer analyzerWithDifferentCars({BMW_M3, AUDI_A6, AUDI_A6});

        std::vector<GroupedCarsByManufacturerAndModel> groupedCars =
            analyzerWithDifferentCars.getGroupedCarsByManufacturerAndModel();
        CHECK(groupedCars.size() == 2);

        CHECK(groupedCars[0].count == 2);
        CHECK(groupedCars[0].manufacturer == "Audi");
        CHECK(groupedCars[0].model == "A6");

        CHECK(groupedCars[1].count == 1);
        CHECK(groupedCars[1].manufacturer == "BMW");
        CHECK(groupedCars[1].model == "M3");
    }

    TEST_CASE_FIXTURE(
        test::helper::ManyCarsFixture,
        "CarsAnalyzer::getGroupedCarsByManufacturerAndModel groups cars by "
        "manufacturer and model within time constraints [unit][performance]" *
            doctest::timeout(1)) {
        CarsAnalyzer analyzerWithManyCars(getManyCars());
        std::vector<GroupedCarsByManufacturerAndModel> groupedCars =
            analyzerWithManyCars.getGroupedCarsByManufacturerAndModel();
        CHECK(groupedCars.size() == 2);

        CHECK(groupedCars[0].count == getNumCars() / 2);
        CHECK(groupedCars[0].manufacturer == "Audi");
        CHECK(groupedCars[0].model == "A6");

        CHECK(groupedCars[1].count == getNumCars() / 2);
        CHECK(groupedCars[1].manufacturer == "BMW");
        CHECK(groupedCars[1].model == "X5");
    }
}
