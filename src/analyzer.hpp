#pragma once

#include <vector>
#include <chrono>
#include "types.hpp"

class CarsAnalyzer
{
public:
    CarsAnalyzer(const std::vector<Car> &cars);
    void setCars(const std::vector<Car> &cars);
    void setWeights(
        float weightHorsePower,
        float weightPrice,
        float weightMileage,
        float weightAge,
        float preferredAge,
        float weightAdvertisementAge,
        float preferredAdvertisementAge);
    void setFilters(
        const std::vector<std::string> &filterByManufacturers,
        const std::vector<std::string> &filterByModels);

    std::vector<ScoredCar> getScoredCars();
    std::vector<GroupedCarsByManufacturerAndModel> getGroupedCars();

private:
    std::vector<Car> cars;
    std::chrono::system_clock::time_point currentTimestamp;

    float weightHorsePower = 1.0f;
    float weightPrice = -1.0f;
    float weightMileage = -1.0f;
    float weightAge = -1.0f;
    float preferredAge = 0.0f;
    float weightAdvertisementAge = -0.0f;
    float preferredAdvertisementAge = 0.0f;
    std::vector<std::string> filterByManufacturers;
    std::vector<std::string> filterByModels;

    int minHorsePower = INT_MAX;
    int maxHorsePower = 0;
    int minPrice = INT_MAX;
    int maxPrice = 0;
    int minMileage = INT_MAX;
    int maxMileage = 0;
    int minAge = INT_MAX;
    int maxAge = 0;
    int minAdvertisementAge = INT_MAX;
    int maxAdvertisementAge = 0;

    void calculateMinMaxValues();
    bool filterCar(const Car &car);
    float scoreCar(const Car &car);
};
