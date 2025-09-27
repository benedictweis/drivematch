#include "doctest/doctest.h"
#include "helper.hpp"
#include "service.hpp"

#include <iostream>

TEST_SUITE("MobileDeCarsScraper Test Suite") {
    TEST_CASE(
        "MobileDeCarsScraper::scrape returns cars for a known good URL "
        "[component]") {
        MobileDeCarsScraper scraper;
        std::vector<Car> cars =
            scraper.scrape("https://suchen.mobile.de/fahrzeuge/search.html?asl=true&cn=DE&dam=false&gn=68766%2C+Hockenheim%2C+Baden-Württemberg&isSearchRequest=true&ll=49.3261824%2C8.5186845&ms=3500%3B322%3B%3B&rd=100&ref=quickSearch&s=Car&vc=Car");
        CHECK(cars.size() > 0);

        for (const auto& car : cars) {
            std::cout << "Provider ID : " << car.providerId << std::endl;
            std::cout << "Timestamp : " << std::chrono::duration_cast<std::chrono::seconds>(car.timestamp.time_since_epoch()).count() << std::endl;
            std::cout << "Manufacturer : " << car.manufacturer << std::endl;
            std::cout << "Model : " << car.model << std::endl;
            std::cout << "Description : " << car.description << std::endl;
            std::cout << "Price : " << car.price << std::endl;
            std::cout << "Attributes : ";
            for (const auto& attr : car.attributes) {
                std::cout << attr << ", ";
            }
            std::cout << std::endl;
            std::cout << "First Registration : " << std::chrono::duration_cast<std::chrono::seconds>(car.firstRegistration.time_since_epoch()).count() << std::endl;
            std::cout << "Mileage : " << car.mileage << std::endl;
            std::cout << "Horse Power : " << car.horsePower << std::endl;
            std::cout << "Fuel Type : " << car.fuelType << std::endl;
            std::cout << "Advertised Since : " << std::chrono::duration_cast<std::chrono::seconds>(car.advertisedSince.time_since_epoch()).count() << std::endl;
            std::cout << "Is Private Seller : " << (car.isPrivateSeller ? "true" : "false") << std::endl;
            std::cout << "Details URL : " << car.detailsURL << std::endl;
            std::cout << "Image URL : " << car.imageURL << std::endl;
            std::cout << "----------------------------------------" << std::endl;
        }
    }
}