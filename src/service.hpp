#pragma once

#include <string>
#include <vector>

#include "analyzer.hpp"
#include "repository.hpp"
#include "types.hpp"

class DriveMatchService {
   public:
    DriveMatchService(CarsSearchRepository& carsSearchRepository,
                      CarsAnalyzer& carsAnalyzer);
    ~DriveMatchService() = default;

    std::vector<Search> getSearches();
    std::vector<ScoredCar> getScoredCarsForSearch(std::string searchId);
    std::vector<GroupedCarsByManufacturerAndModel> getGroupedCarsForSearch(
        std::string searchId);

   private:
    const CarsSearchRepository& carsSearchRepository;
    const CarsAnalyzer& carsAnalyzer;
};
