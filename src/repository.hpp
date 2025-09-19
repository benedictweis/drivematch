#pragma once

#include <string>
#include <vector>

#include "types.hpp"

class CarsSearchRepository {
   public:
    CarsSearchRepository(std::string databasePath);
    virtual ~CarsSearchRepository() = default;

    virtual std::vector<Search> getSearches();
    virtual std::vector<Car> getCarsForSearch(std::string searchId);
};
