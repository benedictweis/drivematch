#include "service.hpp"

#include <string>
#include <vector>

#include "analyzer.hpp"
#include "repository.hpp"
#include "types.hpp"
#include "uuid.hpp"

DriveMatchService::DriveMatchService(CarsScraper& carsScraper, CarsSearchRepository& carsSearchRepository,
                                     CarsAnalyzer& carsAnalyzer)
    : carsScraper(carsScraper), carsSearchRepository(carsSearchRepository), carsAnalyzer(carsAnalyzer) {}

std::string DriveMatchService::scrapeAndStoreCars(std::string name, std::string url) {
    std::vector<Car> cars = carsScraper.scrape(url);
    std::string searchId = generateUUID();
    carsSearchRepository.insertCarsForSearch(searchId, name, url, cars);
    return searchId;
}

std::vector<Search> DriveMatchService::getSearches() {
    return carsSearchRepository.getSearches();
}

std::vector<ScoredCar> DriveMatchService::getScoredCarsForSearch(std::string searchId) {
    std::vector<Car> cars = carsSearchRepository.getCarsForSearch(searchId);
    carsAnalyzer.setCars(cars);
    return carsAnalyzer.getScoredCars();
}

std::vector<GroupedCarsByManufacturerAndModel> DriveMatchService::getGroupedCarsForSearch(std::string searchId) {
    std::vector<Car> cars = carsSearchRepository.getCarsForSearch(searchId);
    carsAnalyzer.setCars(cars);
    return carsAnalyzer.getGroupedCarsByManufacturerAndModel();
}