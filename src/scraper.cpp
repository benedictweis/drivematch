#include "scraper.hpp"

#include <array>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <nlohmann/json.hpp>
#include <stdexcept>
#include <string>

std::vector<Car> MobileDeCarsScraper::scrape(std::string url) {
    std::string command = "./python/dist/scraping/scraping \"" + url + "\"";
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"),
                                                  pclose);
    if (!pipe) {
        throw std::runtime_error("popen() failed!");
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    auto json_data = nlohmann::json::parse(result);

    std::vector<Car> cars;

    for (const auto &item : json_data) {
        Car car{
            .providerId = item.value("providerId", ""),
            .timestamp = std::chrono::system_clock::from_time_t(
                item.value("timestamp", 0)),
            .manufacturer = item.value("manufacturer", ""),
            .model = item.value("model", ""),
            .description = item.value("description", ""),
            .price = item.value("price", 0),
            .attributes = item.value("attributes", std::vector<std::string>{}),
            .firstRegistration = std::chrono::system_clock::from_time_t(
                item.value("firstRegistration", 0)),
            .mileage = item.value("mileage", 0),
            .horsePower = item.value("horsePower", 0),
            .fuelType = item.value("fuelType", ""),
            .advertisedSince = std::chrono::system_clock::from_time_t(
                item.value("advertisedSince", 0)),
            .isPrivateSeller = item.value("isPrivateSeller", false),
            .detailsURL = item.value("detailsURL", ""),
            .imageURL = item.value("imageURL", "")};
        cars.push_back(car);
    }

    return cars;
}