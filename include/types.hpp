#pragma once

#include <chrono>
#include <string>

struct Search {
    std::string id;
    std::string name;
    std::string url;
    std::chrono::system_clock::time_point timestamp;
    int amountOfCars;
};

struct Car {
    std::string providerId;
    std::chrono::system_clock::time_point timestamp;
    std::string manufacturer;
    std::string model;
    std::string description;
    int price;
    std::vector<std::string> attributes;
    std::chrono::system_clock::time_point firstRegistration;
    int mileage;
    int horsePower;
    std::string fuelType;
    std::chrono::system_clock::time_point advertisedSince;
    bool isPrivateSeller;
    std::string detailsURL;
    std::string imageURL;
};

struct ScoredCar {
    Car car;
    float score;
};

struct GroupedCarsByManufacturerAndModel {
    std::string manufacturer;
    std::string model;
    int count;
    float averagePrice;
    float averageMileage;
    float averageHorsePower;
    float averageAge;
    float averageAdvertisementAge;
    std::vector<Car> cars;
};
