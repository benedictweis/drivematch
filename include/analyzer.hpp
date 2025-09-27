#pragma once

#include <chrono>
#include <vector>

#include "types.hpp"

class CarsAnalyzer {
   public:
    virtual ~CarsAnalyzer() = default;
    virtual void setCars(const std::vector<Car> &cars) = 0;
    virtual void setWeights(const AnalyzerWeights &weights) = 0;
    virtual void setFilters(const AnalyzerFilters &filters) = 0;

    virtual std::vector<ScoredCar> getScoredCars() = 0;
    virtual std::vector<GroupedCarsByManufacturerAndModel>
    getGroupedCarsByManufacturerAndModel() = 0;
};
