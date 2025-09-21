#include "repository.hpp"

#include <string>
#include <vector>

#include "types.hpp"

SQLiteCarSearchRepository::SQLiteCarSearchRepository(std::string databasePath) {}

std::vector<Search> SQLiteCarSearchRepository::getSearches() {
    return std::vector<Search>{};
}

std::vector<Car> SQLiteCarSearchRepository::getCarsForSearch(std::string searchId) {
    return std::vector<Car>{};
}