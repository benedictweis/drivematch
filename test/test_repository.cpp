#include <iostream>

#include "doctest/doctest.h"
#include "helper.hpp"
#include "repository.hpp"

TEST_SUITE("SQLiteCarSearchRepository Test Suite") {
    TEST_CASE_FIXTURE(test::helper::ManyCarsFixture,
                      "SQLiteCarSearchRepository::insertCarsForSearch inserts "
                      "cars into the database and returns them "
                      "within time constraints [unit][performance]" *
                          doctest::timeout(2)) {
        SQLiteCarSearchRepository repository(":memory:");
        const std::string searchId = "test_search";
        const std::string name = "Test Search";
        const std::string url = "http://example.com/test_search";
        repository.insertCarsForSearch(searchId, name, url, getManyCars());

        std::vector<Search> searches = repository.getSearches();
        CHECK(searches.size() == 1);
        CHECK(searches[0].id == searchId);
        CHECK(searches[0].name == name);
        CHECK(searches[0].url == url);
        CHECK(searches[0].amountOfCars == getNumCars());

        std::vector<Car> cars = repository.getCarsForSearch(searchId);
        CHECK(cars.size() == getNumCars());
    }

    TEST_CASE(
        "SQLiteCarSearchRepository::insertCarsForSearch inserts "
        "cars into the database and returns them [unit]") {
        SQLiteCarSearchRepository repository(":memory:");
        const std::string searchId = "test_search";
        const std::string name = "Test Search";
        const std::string url = "http://example.com/test_search";
        repository.insertCarsForSearch(searchId, name, url, {test::helper::WORST_CAR, test::helper::BEST_CAR});

        std::vector<Search> searches = repository.getSearches();
        CHECK(searches.size() == 1);
        CHECK(searches[0].id == searchId);
        CHECK(searches[0].name == name);
        CHECK(searches[0].url == url);
        CHECK(searches[0].amountOfCars == 2);

        std::vector<Car> cars = repository.getCarsForSearch(searchId);
        CHECK(cars.size() == 2);

        CHECK_EQ(cars[0].providerId, test::helper::WORST_CAR.providerId);
        CHECK_EQ(std::chrono::duration_cast<std::chrono::seconds>(cars[0].timestamp.time_since_epoch()).count(), 
             std::chrono::duration_cast<std::chrono::seconds>(test::helper::WORST_CAR.timestamp.time_since_epoch()).count());
        CHECK_EQ(cars[0].manufacturer, test::helper::WORST_CAR.manufacturer);
        CHECK_EQ(cars[0].model, test::helper::WORST_CAR.model);
        CHECK_EQ(cars[0].description, test::helper::WORST_CAR.description);
        CHECK_EQ(cars[0].price, test::helper::WORST_CAR.price);
        CHECK_EQ(cars[0].attributes, test::helper::WORST_CAR.attributes);
        CHECK_EQ(std::chrono::duration_cast<std::chrono::seconds>(cars[0].firstRegistration.time_since_epoch()).count(), 
             std::chrono::duration_cast<std::chrono::seconds>(test::helper::WORST_CAR.firstRegistration.time_since_epoch()).count());
        CHECK_EQ(cars[0].mileage, test::helper::WORST_CAR.mileage);
        CHECK_EQ(cars[0].horsePower, test::helper::WORST_CAR.horsePower);
        CHECK_EQ(cars[0].fuelType, test::helper::WORST_CAR.fuelType);
        CHECK_EQ(std::chrono::duration_cast<std::chrono::seconds>(cars[0].advertisedSince.time_since_epoch()).count(), 
             std::chrono::duration_cast<std::chrono::seconds>(test::helper::WORST_CAR.advertisedSince.time_since_epoch()).count());
        CHECK_EQ(cars[0].isPrivateSeller, test::helper::WORST_CAR.isPrivateSeller);
        CHECK_EQ(cars[0].detailsURL, test::helper::WORST_CAR.detailsURL);
        CHECK_EQ(cars[0].imageURL, test::helper::WORST_CAR.imageURL);

        CHECK_EQ(cars[1].providerId, test::helper::BEST_CAR.providerId);
        CHECK_EQ(std::chrono::duration_cast<std::chrono::seconds>(cars[1].timestamp.time_since_epoch()).count(), 
             std::chrono::duration_cast<std::chrono::seconds>(test::helper::BEST_CAR.timestamp.time_since_epoch()).count());
        CHECK_EQ(cars[1].manufacturer, test::helper::BEST_CAR.manufacturer);
        CHECK_EQ(cars[1].model, test::helper::BEST_CAR.model);
        CHECK_EQ(cars[1].description, test::helper::BEST_CAR.description);
        CHECK_EQ(cars[1].price, test::helper::BEST_CAR.price);
        CHECK_EQ(cars[1].attributes, test::helper::BEST_CAR.attributes);
        CHECK_EQ(std::chrono::duration_cast<std::chrono::seconds>(cars[1].firstRegistration.time_since_epoch()).count(), 
             std::chrono::duration_cast<std::chrono::seconds>(test::helper::BEST_CAR.firstRegistration.time_since_epoch()).count());
        CHECK_EQ(cars[1].mileage, test::helper::BEST_CAR.mileage);
        CHECK_EQ(cars[1].horsePower, test::helper::BEST_CAR.horsePower);
        CHECK_EQ(cars[1].fuelType, test::helper::BEST_CAR.fuelType);
        CHECK_EQ(std::chrono::duration_cast<std::chrono::seconds>(cars[1].advertisedSince.time_since_epoch()).count(), 
             std::chrono::duration_cast<std::chrono::seconds>(test::helper::BEST_CAR.advertisedSince.time_since_epoch()).count());
        CHECK_EQ(cars[1].isPrivateSeller, test::helper::BEST_CAR.isPrivateSeller);
        CHECK_EQ(cars[1].detailsURL, test::helper::BEST_CAR.detailsURL);
        CHECK_EQ(cars[1].imageURL, test::helper::BEST_CAR.imageURL);
    }
}