#include <iostream>

#include "doctest/doctest.h"
#include "helper.hpp"
#include "repository.hpp"

TEST_SUITE("SQLiteCarSearchRepository Test Suite") {
    TEST_CASE_FIXTURE(test::helper::ManyCarsFixture,
                      "SQLiteCarSearchRepository::insertCarsForSearch inserts "
                      "cars into the database and returns them "
                      "within time constraints" *
                          doctest::timeout(1.5)) {
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
}