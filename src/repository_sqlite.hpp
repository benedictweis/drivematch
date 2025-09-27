#pragma once

#include <SQLiteCpp/SQLiteCpp.h>

#include <string>
#include <vector>

#include "types.hpp"
#include "repository.hpp"

class SQLiteCarSearchRepository : public CarsSearchRepository {
   public:
    SQLiteCarSearchRepository(std::string databasePath);
    ~SQLiteCarSearchRepository() override = default;

    void insertCarsForSearch(std::string searchId, std::string name,
                             std::string url, std::vector<Car> cars) override;
    std::vector<Search> getSearches() override;
    std::vector<Car> getCarsForSearch(std::string searchId) override;

   private:
    std::unique_ptr<SQLite::Database> database;
    std::unique_ptr<SQLite::Statement> insertSearchStmt;
    std::unique_ptr<SQLite::Statement> insertCarStmt;
    std::unique_ptr<SQLite::Statement> insertSearchesCarsStmt;
    std::unique_ptr<SQLite::Statement> getSearchesStmt;
    std::unique_ptr<SQLite::Statement> getCarsForSearchStmt;

    int serializeTimePoint(std::chrono::system_clock::time_point tp);
    std::string serializeAttributes(const std::vector<std::string>& attributes);

    std::chrono::system_clock::time_point deserializeTimePoint(int time);
    std::vector<std::string> deserializeAttributes(const std::string& attributesStr);
};
