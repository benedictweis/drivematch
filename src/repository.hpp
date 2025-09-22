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
};
