#pragma once
#include <string>

#include "types.hpp"
#include "uuid.hpp"

namespace test {
namespace helper {

const Car WORSE_CAR = Car{
    .providerId = "worst_car",
    .timestamp = std::chrono::system_clock::now(),
    .manufacturer = "WorstManufacturer",
    .model = "WorstModel",
    .description = "The worst car ever",
    .price = 100000,  // Very high price
    .attributes = {"old", "broken"},
    .firstRegistration = std::chrono::system_clock::now() -
                         std::chrono::hours(24 * 365 * 20),  // 20 years old
    .mileage = 500000,  // Very high mileage
    .horsePower = 50,   // Very low horsepower
    .fuelType = "Gasoline",
    .advertisedSince = std::chrono::system_clock::now() -
                       std::chrono::hours(24 * 365),  // Advertised for a year
    .isPrivateSeller = true,
    .detailsURL = "http://example.com/worst_car",
    .imageURL = "http://example.com/worst_car/image"};

const Car BEST_CAR =
    Car{.providerId = "best_car",
        .timestamp = std::chrono::system_clock::now(),
        .manufacturer = "BestManufacturer",
        .model = "BestModel",
        .description = "The best car ever",
        .price = 20000,  // Reasonable price
        .attributes = {"new", "fast"},
        .firstRegistration = std::chrono::system_clock::now() -
                             std::chrono::hours(24 * 30),  // 1 month old
        .mileage = 1000,                                   // Very low mileage
        .horsePower = 400,  // Very high horsepower
        .fuelType = "Gasoline",
        .advertisedSince = std::chrono::system_clock::now() -
                           std::chrono::hours(24 * 5),  // Advertised for 5 days
        .isPrivateSeller = false,
        .detailsURL = "http://example.com/best_car",
        .imageURL = "http://example.com/best_car/image"};

inline Car generateRandomCarWithManufacturerAndModel(const std::string &manufacturer,
                                              const std::string &model) {
    static std::chrono::system_clock::time_point now =
        std::chrono::system_clock::now();
    static std::random_device rd;
    static std::mt19937_64 gen(rd());
    static std::uniform_int_distribution<uint64_t> dis;

    return Car{
        .providerId = generateUUID(),
        .timestamp = now,
        .manufacturer = manufacturer,
        .model = model,
        .description = "A random car",
        .price = static_cast<int>(dis(gen) % 50000 +
                                  5000),  // Price between 5000 and 55000
        .attributes = {"attribute1", "attribute2"},
        .firstRegistration =
            now -
            std::chrono::hours(24 * (dis(gen) % 3650)),  // Up to 10 years old
        .mileage = static_cast<int>(dis(gen) % 200000),  // Up to 200,000 km
        .horsePower =
            static_cast<int>(dis(gen) % 400 + 50),  // Between 50 and 450 HP
        .fuelType = "Gasoline",
        .advertisedSince =
            now -
            std::chrono::hours(24 * (dis(gen) % 60)),  // Up to 60 days ago
        .isPrivateSeller = dis(gen) % 2 == 0,
        .detailsURL = "http://example.com/car/" + generateUUID(),
        .imageURL = "http://example.com/car/image/" + generateUUID(),
    };
}

class ManyCarsFixture {
   private:
    static std::vector<Car> manyCars;
    static bool initialized;
    const int numCars = 100000;

   public:
    ManyCarsFixture() {
        if (initialized) return;
        this->manyCars.reserve(this->numCars);
        for (int i = 0; i < numCars / 2; ++i) {
            this->manyCars.push_back(
                generateRandomCarWithManufacturerAndModel("BMW", "X5"));
            this->manyCars.push_back(
                generateRandomCarWithManufacturerAndModel("Audi", "A6"));
        }
        initialized = true;
    }

    const int &getNumCars() const { return this->numCars; }

    const std::vector<Car> &getManyCars() const { return this->manyCars; }
};

inline std::vector<Car> ManyCarsFixture::manyCars;
inline bool ManyCarsFixture::initialized = false;

}  // namespace helper
}  // namespace test
