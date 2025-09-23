#pragma once

#include <string>
#include <vector>

#include "analyzer.hpp"
#include "repository.hpp"
#include "scraper.hpp"
#include "types.hpp"

class DriveMatchService {
   public:
    DriveMatchService(CarsScraper& carsScraper,
                      CarsSearchRepository& carsSearchRepository,
                      CarsAnalyzer& carsAnalyzer);
    ~DriveMatchService() = default;
    
    std::string scrapeAndStoreCars(std::string name, std::string url);
    std::vector<Search> getSearches();
    std::vector<ScoredCar> getScoredCarsForSearch(std::string searchId);
    std::vector<GroupedCarsByManufacturerAndModel> getGroupedCarsForSearch(
        std::string searchId);

   private:
    CarsScraper& carsScraper;
    CarsSearchRepository& carsSearchRepository;
    CarsAnalyzer& carsAnalyzer;
};
