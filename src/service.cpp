#include "service.hpp"

#include <string>
#include <vector>

#include "analyzer.hpp"
#include "repository.hpp"
#include "types.hpp"

DriveMatchService::DriveMatchService(CarsSearchRepository carsSearchRepository,
                                     CarsAnalyzer carsAnalyzer)
    : carsSearchRepository(carsSearchRepository), carsAnalyzer(carsAnalyzer) {}
