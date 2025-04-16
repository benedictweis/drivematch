import uuid

from api.analysis import CarsAnalyzer
from api.scraping import CarsScraper
from api.car import GroupedCarsByManufacturerAndModel, ScoredCar
from api.db import SearchInfo, SearchesRepository


def create_default_drivematch_service(db_path: str):
    from api.db import SQLiteSearchesRepository
    from api.scraping import MobileDeScraper
    from api.analysis import CarsAnalyzer

    return DriveMatchService(
        SQLiteSearchesRepository(db_path),
        MobileDeScraper(),
        CarsAnalyzer()
    )


class DriveMatchService():
    def __init__(
        self,
        searches_repository: SearchesRepository,
        cars_scraper: CarsScraper,
        cars_analyzer: CarsAnalyzer
    ):
        self.searches_repository = searches_repository
        self.cars_scraper = cars_scraper
        self.cars_analyzer = cars_analyzer

    def scrape(self, name: str, url: str):
        cars = self.cars_scraper.scrape(url)
        search_id = str(uuid.uuid4())
        self.searches_repository.insert_cars_for_search(
            search_id, name, url, cars
        )

    def get_scores(
        self,
        search_id: str,
        weight_horsepower: float,
        weight_price: float,
        weight_mileage: float,
        weight_age: float,
        preferred_age: float,
        filter_by_manufacturer: str,
        filter_by_model: str,
    ) -> list[ScoredCar]:
        cars = self.searches_repository.get_cars_for_search(search_id)
        self.cars_analyzer.set_cars(cars)
        self.cars_analyzer.set_weights_and_filters(
            weight_horsepower,
            weight_price,
            weight_mileage,
            weight_age,
            preferred_age,
            filter_by_manufacturer,
            filter_by_model,
        )
        return self.cars_analyzer.get_scored_cars()

    def get_groups(
        self, search_id: str
    ) -> list[GroupedCarsByManufacturerAndModel]:
        cars = self.searches_repository.get_cars_for_search(search_id)
        self.cars_analyzer.set_cars(cars)
        return self.cars_analyzer.get_grouped_cars()

    def get_searches(self) -> list[SearchInfo]:
        return self.searches_repository.get_searches()
