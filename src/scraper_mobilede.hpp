#pragma once

#include <string>

#include "types.hpp"
#include "scraper.hpp"

class MobileDeCarsScraper: public CarsScraper {
    public:
        ~MobileDeCarsScraper() override = default;
        std::vector<Car> scrape(std::string url) override;
};