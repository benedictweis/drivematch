#include "repository.hpp"

#include <SQLiteCpp/SQLiteCpp.h>

#include <chrono>
#include <string>
#include <vector>

#include "types.hpp"
#include "uuid.hpp"

SQLiteCarSearchRepository::SQLiteCarSearchRepository(std::string databasePath) {
    this->database = std::make_unique<SQLite::Database>(SQLite::Database(
        databasePath, SQLite::OPEN_READWRITE | SQLite::OPEN_CREATE));

    this->database->exec(
        "CREATE TABLE IF NOT EXISTS searches (id TEXT PRIMARY KEY, name "
        "TEXT, url TEXT, timestamp DATETIME);"
        "CREATE TABLE IF NOT EXISTS cars (id TEXT PRIMARY KEY, provider_id "
        "TEXT, timestamp DATETIME, manufacturer TEXT, model TEXT, "
        "description TEXT, price INTEGER, attributes TEXT, firstRegistration "
        "DATETIME, mileage INTEGER, horsePower INTEGER, fuelType TEXT, "
        "advertisedSince DATETIME, privateSeller INTEGER, detailsURL TEXT, "
        "imageURL TEXT);"
        "CREATE TABLE IF NOT EXISTS searches_cars (search_id TEXT, car_id "
        "TEXT, FOREIGN KEY (search_id) REFERENCES searches(id), FOREIGN KEY "
        "(car_id) REFERENCES cars(id));");

    this->insertSearchStmt =
        std::make_unique<SQLite::Statement>(*this->database,
                                            "INSERT INTO searches (id, name, "
                                            "url, timestamp) VALUES "
                                            "(?, ?, ?, ?)");
    this->insertCarStmt = std::make_unique<SQLite::Statement>(
        *this->database,
        "INSERT INTO cars (id, provider_id, timestamp, manufacturer, model,"
        "description, price, attributes, firstRegistration, mileage,"
        "horsePower, fuelType, advertisedSince, privateSeller,"
        "detailsURL, imageURL)"
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
    this->insertSearchesCarsStmt = std::make_unique<SQLite::Statement>(
        *this->database,
        "INSERT INTO searches_cars (search_id, car_id) VALUES (?, ?)");
    this->getSearchesStmt = std::make_unique<SQLite::Statement>(
        *this->database,
        "SELECT searches.id, searches.name, searches.url, "
        "searches.timestamp, COUNT(searches_cars.car_id) as amount_of_cars "
        "FROM searches LEFT JOIN searches_cars ON searches.id = "
        "searches_cars.search_id GROUP BY searches.id, searches.name, "
        "searches.url, searches.timestamp");

    this->getCarsForSearchStmt = std::make_unique<SQLite::Statement>(
        *this->database,
        "SELECT cars.* FROM cars INNER JOIN searches_cars ON cars.id = "
        "searches_cars.car_id WHERE searches_cars.search_id = ?");
}

void SQLiteCarSearchRepository::insertCarsForSearch(std::string searchId,
                                                    std::string name,
                                                    std::string url,
                                                    std::vector<Car> cars) {
    SQLite::Transaction transaction(*this->database);

    int currentTimeInSecondsSinceEpoch = static_cast<int>(
        std::chrono::system_clock::to_time_t(std::chrono::system_clock::now()));

    this->insertSearchStmt->bind(1, searchId);
    this->insertSearchStmt->bind(2, name);
    this->insertSearchStmt->bind(3, url);
    this->insertSearchStmt->bind(4, currentTimeInSecondsSinceEpoch);

    this->insertSearchStmt->exec();
    this->insertSearchStmt->reset();

    for (int i = 0; i < cars.size(); ++i) {
        const Car &car = cars[i];
        const std::string &carUUID = generateUUID();

        this->insertCarStmt->bind(1, carUUID);
        this->insertCarStmt->bind(2, car.providerId);
        this->insertCarStmt->bind(
            3, static_cast<int>(
                   std::chrono::system_clock::to_time_t(car.timestamp)));
        this->insertCarStmt->bind(4, car.manufacturer);
        this->insertCarStmt->bind(5, car.model);
        this->insertCarStmt->bind(6, car.description);
        this->insertCarStmt->bind(7, car.price);
        // Join attributes vector into a comma-separated string
        std::string attributesStr;
        for (size_t j = 0; j < car.attributes.size(); ++j)
            attributesStr +=
                car.attributes[j] + (j < car.attributes.size() - 1 ? "," : "");
        this->insertCarStmt->bind(8, attributesStr);
        this->insertCarStmt->bind(
            9, static_cast<int>(std::chrono::system_clock::to_time_t(
                   car.firstRegistration)));
        this->insertCarStmt->bind(10, car.mileage);
        this->insertCarStmt->bind(11, car.horsePower);
        this->insertCarStmt->bind(12, car.fuelType);
        this->insertCarStmt->bind(
            13, static_cast<int>(
                    std::chrono::system_clock::to_time_t(car.advertisedSince)));
        this->insertCarStmt->bind(14, car.isPrivateSeller ? 1 : 0);
        this->insertCarStmt->bind(15, car.detailsURL);
        this->insertCarStmt->bind(16, car.imageURL);

        this->insertCarStmt->exec();
        this->insertCarStmt->reset();

        this->insertSearchesCarsStmt->bind(1, searchId);
        this->insertSearchesCarsStmt->bind(2, carUUID);

        this->insertSearchesCarsStmt->exec();
        this->insertSearchesCarsStmt->reset();
    }

    transaction.commit();
}

std::vector<Search> SQLiteCarSearchRepository::getSearches() {
    std::vector<Search> searches;

    while (this->getSearchesStmt->executeStep()) {
        Search search{
            .id = this->getSearchesStmt->getColumn(0).getString(),
            .name = this->getSearchesStmt->getColumn(1).getString(),
            .url = this->getSearchesStmt->getColumn(2).getString(),
            .timestamp = std::chrono::system_clock::from_time_t(
                this->getSearchesStmt->getColumn(3).getInt()),
            .amountOfCars = this->getSearchesStmt->getColumn(4).getInt()};
        searches.push_back(search);
    }

    this->getSearchesStmt->reset();

    return searches;
}

std::vector<Car> SQLiteCarSearchRepository::getCarsForSearch(
    std::string searchId) {
    std::vector<Car> cars;

    this->getCarsForSearchStmt->bind(1, searchId);

    while (this->getCarsForSearchStmt->executeStep()) {
        Car car{
            .providerId = this->getCarsForSearchStmt->getColumn(1).getString(),
            .timestamp = std::chrono::system_clock::from_time_t(
                this->getCarsForSearchStmt->getColumn(2).getInt()),
            .manufacturer =
                this->getCarsForSearchStmt->getColumn(3).getString(),
            .model = this->getCarsForSearchStmt->getColumn(4).getString(),
            .description = this->getCarsForSearchStmt->getColumn(5).getString(),
            .price = this->getCarsForSearchStmt->getColumn(6).getInt(),
            .attributes = 
                [this]() {
                    std::vector<std::string> attrs;
                    std::string attributesStr =
                        this->getCarsForSearchStmt->getColumn(7).getString();
                    if (!attributesStr.empty()) {
                        size_t start = 0;
                        size_t end = attributesStr.find(',');
                        while (end != std::string::npos) {
                            attrs.push_back(
                                attributesStr.substr(start, end - start));
                            start = end + 1;
                            end = attributesStr.find(',', start);
                        }
                        attrs.push_back(attributesStr.substr(start));
                    }
                    return attrs;
                }(),
            .firstRegistration = std::chrono::system_clock::from_time_t(
                this->getCarsForSearchStmt->getColumn(8).getInt()),
            .mileage = this->getCarsForSearchStmt->getColumn(9).getInt(),
            .horsePower = this->getCarsForSearchStmt->getColumn(10).getInt(),
            .fuelType = this->getCarsForSearchStmt->getColumn(11).getString(),
            .advertisedSince = std::chrono::system_clock::from_time_t(
                this->getCarsForSearchStmt->getColumn(12).getInt()),
            .isPrivateSeller =
                this->getCarsForSearchStmt->getColumn(13).getInt() == 1,
            .detailsURL = this->getCarsForSearchStmt->getColumn(14).getString(),
            .imageURL = this->getCarsForSearchStmt->getColumn(15).getString()};
        cars.push_back(car);
    }

    this->getCarsForSearchStmt->reset();

    return cars;
}
