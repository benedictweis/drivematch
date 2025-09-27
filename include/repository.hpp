#pragma once

#include <SQLiteCpp/SQLiteCpp.h>

#include <string>
#include <vector>

#include "types.hpp"

class CarsSearchRepository {
   public:
    virtual ~CarsSearchRepository() = default;

    virtual void insertCarsForSearch(std::string searchId, std::string name,
                                     std::string url,
                                     std::vector<Car> cars) = 0;
    virtual std::vector<Search> getSearches() = 0;
    virtual std::vector<Car> getCarsForSearch(std::string searchId) = 0;
};
