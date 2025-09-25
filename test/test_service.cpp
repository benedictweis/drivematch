#include "doctest/doctest.h"
#include "helper.hpp"
#include "service.hpp"

TEST_SUITE("DriveMatchService Test Suite") {
    TEST_CASE_FIXTURE(
        test::helper::ManyCarsFixture,
        "DriveMatchService returns expected results within time constraints "
        "[component][performance]" *
            doctest::timeout(2.5)) {
        MobileDeCarsScraper scraper;
        SQLiteCarSearchRepository repository(":memory:");
        CarsAnalyzer analyzer;
        DriveMatchService service(scraper, repository, analyzer);

        const std::string searchId = "test_search";
        const std::string name = "Test Search";
        const std::string url = "http://example.com/test_search";
        repository.insertCarsForSearch(searchId, name, url, getManyCars());

        std::vector<Search> searches = service.getSearches();
        CHECK(searches.size() == 1);
        CHECK(searches[0].id == searchId);
        CHECK(searches[0].name == name);
        CHECK(searches[0].url == url);
        CHECK(searches[0].amountOfCars == getNumCars());

        std::vector<ScoredCar> cars = service.getScoredCarsForSearch(searchId);
        CHECK(cars.size() == getNumCars());

        std::vector<GroupedCarsByManufacturerAndModel> groupedCars =
            service.getGroupedCarsForSearch(searchId);
        CHECK(groupedCars.size() == 2);
    }

    TEST_CASE(
        "DriveMatchService returns expected results within time constraints "
        "[unit]") {
        MobileDeCarsScraper scraper;
        SQLiteCarSearchRepository repository(":memory:");
        CarsAnalyzer analyzer;
        DriveMatchService service(scraper, repository, analyzer);

        const std::string searchId = "test_search";
        const std::string name = "Test Search";
        const std::string url = "http://example.com/test_search";
        repository.insertCarsForSearch(searchId, name, url, {test::helper::WORST_CAR, test::helper::BEST_CAR});

        std::vector<Search> searches = service.getSearches();
        CHECK(searches.size() == 1);
        CHECK(searches[0].id == searchId);
        CHECK(searches[0].name == name);
        CHECK(searches[0].url == url);
        CHECK(searches[0].amountOfCars == 2);

        std::vector<ScoredCar> scoredCars = service.getScoredCarsForSearch(searchId);
        CHECK(scoredCars.size() == 2);
        CHECK(scoredCars[0].car.providerId == test::helper::BEST_CAR.providerId);
        CHECK(scoredCars[1].car.providerId == test::helper::WORST_CAR.providerId);

        std::vector<GroupedCarsByManufacturerAndModel> groupedCars =
            service.getGroupedCarsForSearch(searchId);
        CHECK(groupedCars.size() == 2);

        scoredCars = service.getScoredCarsForSearch(searchId, {-1, 1, 1, 1, 100, 1, 100});
        CHECK(scoredCars.size() == 2);
        CHECK(scoredCars[0].car.providerId == test::helper::WORST_CAR.providerId);
        CHECK(scoredCars[1].car.providerId == test::helper::BEST_CAR.providerId);

        scoredCars = service.getScoredCarsForSearch(searchId, {}, {{test::helper::BEST_CAR.manufacturer}, {test::helper::BEST_CAR.model}});
        CHECK(scoredCars.size() == 1);
        CHECK(scoredCars[0].car.providerId == test::helper::BEST_CAR.providerId);
    }
}
