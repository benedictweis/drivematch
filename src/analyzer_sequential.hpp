#pragma once

#include <chrono>
#include <vector>

#include "types.hpp"
#include "analyzer.hpp"

class SequentialCarsAnalyzer: public CarsAnalyzer {
   public:
    SequentialCarsAnalyzer() = default;
    SequentialCarsAnalyzer(const std::vector<Car> &cars);
    ~SequentialCarsAnalyzer() override = default;
    void setCars(const std::vector<Car> &cars) override;
    void setWeights(const AnalyzerWeights &weights) override;
    void setFilters(const AnalyzerFilters &filters) override;

    std::vector<ScoredCar> getScoredCars() override;
    std::vector<GroupedCarsByManufacturerAndModel>
    getGroupedCarsByManufacturerAndModel() override;

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
