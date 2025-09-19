#include "analyzer.hpp"

const float EPSILON = 1e-10;

float normalize(float value, float minValue, float maxValue)
{
    if (maxValue == minValue)
        return 0.0f;
    return (value - minValue + EPSILON) * 100 / (maxValue - minValue + EPSILON);
}

CarsAnalyzer::CarsAnalyzer(const std::vector<Car> &cars) : cars(cars)
{
}

void CarsAnalyzer::setCars(const std::vector<Car> &cars)
{
    this->cars = cars;
}

void CarsAnalyzer::setWeights(
    float weightHp,
    float weightPrice,
    float weightMileage,
    float weightAge,
    float preferredAge,
    float weightAdvertisementAge,
    float preferredAdvertisementAge)
{
    this->weightHorsePower = weightHp;
    this->weightPrice = weightPrice;
    this->weightMileage = weightMileage;
    this->weightAge = weightAge;
    this->preferredAge = preferredAge;
    this->weightAdvertisementAge = weightAdvertisementAge;
    this->preferredAdvertisementAge = preferredAdvertisementAge;
}

void CarsAnalyzer::setFilters(
    const std::vector<std::string> &filterByManufacturers,
    const std::vector<std::string> &filterByModels)
{
    this->filterByManufacturers = filterByManufacturers;
    this->filterByModels = filterByModels;
}

std::vector<ScoredCar> CarsAnalyzer::getScoredCars()
{
    this->currentTimestamp = std::chrono::system_clock::now();
    std::vector<ScoredCar> scoredCars;
    scoredCars.reserve(this->cars.size());
    calculateMinMaxValues();
    for (const Car &car : cars)
    {
        if (filterCar(car))
            continue;
        scoredCars.push_back({.car = car, .score = scoreCar(car)});
    }
    std::sort(scoredCars.begin(), scoredCars.end(),
              [](const ScoredCar &a, const ScoredCar &b)
              {
                  return a.score > b.score;
              });
    return scoredCars;
}

std::vector<GroupedCarsByManufacturerAndModel> CarsAnalyzer::getGroupedCars()
{
    // Group cars by manufacturer and model
    return {};
}

void CarsAnalyzer::calculateMinMaxValues()
{
    minHorsePower = INT_MAX;
    maxHorsePower = 0;
    minPrice = INT_MAX;
    maxPrice = 0;
    minMileage = INT_MAX;
    maxMileage = 0;
    minAge = INT_MAX;
    maxAge = 0;
    minAdvertisementAge = INT_MAX;
    maxAdvertisementAge = 0;

    for (const Car &car : cars)
    {
        if (car.horsePower < minHorsePower)
            minHorsePower = car.horsePower;
        if (car.horsePower > maxHorsePower)
            maxHorsePower = car.horsePower;

        if (car.price < minPrice)
            minPrice = car.price;
        if (car.price > maxPrice)
            maxPrice = car.price;

        if (car.mileage < minMileage)
            minMileage = car.mileage;
        if (car.mileage > maxMileage)
            maxMileage = car.mileage;

        int ageDays = std::chrono::duration_cast<std::chrono::days>(currentTimestamp - car.firstRegistration).count();
        if (ageDays < minAge)
            minAge = ageDays;
        if (ageDays > maxAge)
            maxAge = ageDays;

        int advertisementAgeDays = std::chrono::duration_cast<std::chrono::days>(currentTimestamp - car.advertisedSince).count();
        if (advertisementAgeDays < minAdvertisementAge)
            minAdvertisementAge = advertisementAgeDays;
        if (advertisementAgeDays > maxAdvertisementAge)
            maxAdvertisementAge = advertisementAgeDays;
    }
}

bool CarsAnalyzer::filterCar(const Car &car)
{
    if (!this->filterByManufacturers.empty())
    {
        bool containedInManufacturer = false;
        for (const std::string manufacturer : this->filterByManufacturers)
        {
            if (car.manufacturer == manufacturer)
            {
                containedInManufacturer = true;
            }
        }
        if (!containedInManufacturer)
        {
            return true;
        }
    }
    if (!this->filterByModels.empty())
    {
        bool containedInModel = false;
        for (const std::string model : this->filterByModels)
        {

            if (car.model == model)
            {
                containedInModel = true;
            }
        }
        if (!containedInModel)
        {
            return true;
        }
    }
    return false;
}

float CarsAnalyzer::scoreCar(const Car &car)
{
    int ageDays = std::chrono::duration_cast<std::chrono::days>(currentTimestamp - car.firstRegistration).count();
    int ageDaysDiff = std::abs(ageDays - preferredAge);

    int advertisementAgeDays = std::chrono::duration_cast<std::chrono::days>(currentTimestamp - car.advertisedSince).count();
    int advertisementAgeDaysDiff = std::abs(advertisementAgeDays - preferredAdvertisementAge);

    float normalizedHorsePower = normalize(car.horsePower, minHorsePower, maxHorsePower);
    float normalizedPrice = normalize(car.price, minPrice, maxPrice);
    float normalizedMileage = normalize(car.mileage, minMileage, maxMileage);
    float normalizedAge = normalize(ageDaysDiff, minAge, maxAge);
    float normalizedAdvertisementAge = normalize(advertisementAgeDaysDiff, minAdvertisementAge, maxAdvertisementAge);

    return (weightHorsePower * normalizedHorsePower) +
           (weightPrice * normalizedPrice) +
           (weightMileage * normalizedMileage) +
           (weightAge * normalizedAge) +
           (weightAdvertisementAge * normalizedAdvertisementAge);
}
