#pragma once

#include <string>
#include <vector>

#include "types.hpp"

class CarsSearchRepository {
   public:
    virtual ~CarsSearchRepository() = default;

    virtual std::vector<Search> getSearches() = 0;
    virtual std::vector<Car> getCarsForSearch(std::string searchId) = 0;
};

class SQLiteCarSearchRepository: public CarsSearchRepository {
   public:
    SQLiteCarSearchRepository(std::string databasePath);
    ~SQLiteCarSearchRepository() override = default;

    std::vector<Search> getSearches() override;
    std::vector<Car> getCarsForSearch(std::string searchId) override;
};
