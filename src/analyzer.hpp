#pragma once

#include <chrono>
#include <vector>

#include "types.hpp"

class CarsAnalyzer {
   public:
    CarsAnalyzer() = default;
    CarsAnalyzer(const std::vector<Car> &cars);
    ~CarsAnalyzer() = default;
    void setCars(const std::vector<Car> &cars);
    void setWeights(const AnalyzerWeights &weights);
    void setFilters(const AnalyzerFilters &filters);

    std::vector<ScoredCar> getScoredCars();
    std::vector<GroupedCarsByManufacturerAndModel>
    getGroupedCarsByManufacturerAndModel();

   private:
    std::vector<Car> cars;
    std::chrono::system_clock::time_point currentTimestamp;

    AnalyzerWeights weights{1.0f, -1.0f, -1.0f, -1.0f, 0.0f, 0.0f, 0.0f};
    AnalyzerFilters filters{{}, {}};

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
    bool filterCar(const Car &car) const;
    float scoreCar(const Car &car) const;
};
