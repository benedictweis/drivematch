import cProfile
import datetime
from pathlib import Path
import pstats
import random
import uuid

from drivematch._internal.analysis import CarsAnalyzer
from drivematch._internal.db import SQLiteSearchesRepository
from drivematch._internal.scraping import MobileDeScraper
from drivematch.core import DriveMatchService
from drivematch.types import Car
from drivematch.types import RegressionFunctionType

repository = SQLiteSearchesRepository(":memory:")

drivematch_service = DriveMatchService(
    searches_repository=repository,
    cars_scraper=MobileDeScraper(),
    cars_analyzer=CarsAnalyzer(),
)


def random_car(manufacturer: str, model: str) -> Car:
    return Car(
        id=str(uuid.uuid4()),
        timestamp=datetime.datetime.now(),
        manufacturer=manufacturer,
        model=model,
        description=f"{manufacturer} {model} in excellent condition",
        price=random.randint(15000, 80000),
        attributes=[
            random.choice(
                ["Air Conditioning", "Navigation", "Leather Seats", "Sunroof"]
            )
            for _ in range(random.randint(1, 3))
        ],
        first_registration=datetime.datetime(
            random.randint(2010, 2024), random.randint(1, 12), random.randint(1, 28)
        ),
        mileage=random.randint(10000, 150000),
        horse_power=random.randint(100, 500),
        fuel_type=random.choice(["Gasoline", "Diesel", "Electric", "Hybrid"]),
        advertised_since=datetime.datetime.now()
        - datetime.timedelta(days=random.randint(1, 30)),
        private_seller=random.choice([True, False]),
        details_url=f"https://example.com/car/{random.randint(1000, 9999)}",
        image_url=f"https://example.com/images/car_{random.randint(1000, 9999)}.jpg",
    )


cars = [random_car("BMW", "X5") for _ in range(100000)] + [
    random_car("Audi", "A6") for _ in range(100000)
]

search_id = "search-1"
repository.insert_cars_for_search(
    search_id, "test", "https://example.com/search/1", cars
)


functions = [
    [
        "perf/get_scores.prof",
        lambda: drivematch_service.get_scores(
            search_id, 1, -1, -1, -1, 0, 0, 0, [], []
        ),
    ],
    [
        "perf/get_groups.prof",
        lambda: drivematch_service.get_groups(search_id),
    ],
    [
        "perf/get_regression_line.prof",
        lambda: drivematch_service.get_regression_line(search_id, RegressionFunctionType.POLYNOMIAL_4),
    ]
]

for function in functions:
    with cProfile.Profile() as profiler:
        function[1]()

    stats = pstats.Stats(profiler)
    stats.sort_stats(pstats.SortKey.CUMULATIVE)
    print("Running function:", function[0])
    stats.print_stats("drivematch/drivematch")

    stats.dump_stats(function[0])
