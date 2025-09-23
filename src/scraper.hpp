#pragma once

#include <string>

#include "types.hpp"

class CarsScraper {
public:
    virtual ~CarsScraper() = default;
    virtual std::vector<Car> scrape(std::string url) = 0;
};

class MobileDeCarsScraper: public CarsScraper {
    public:
        ~MobileDeCarsScraper() override = default;
        std::vector<Car> scrape(std::string url) override;
};