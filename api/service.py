import uuid

from api.analysis import CarsAnalyzer
from api.scraping import CarsScraper
from api.car import ScoredAndGroupedCars
from api.db import SearchesRepository


class DriveMatchService():
    def __init__(
        self,
        searches_repository: SearchesRepository,
        cars_scraper: CarsScraper,
        cars_analyzer: CarsAnalyzer
    ):
        self.searchesRepository = searches_repository
        self.carsScraper = cars_scraper
        self.carsAnalyzer = cars_analyzer

    def scrape(self, name: str, url: str):
        cars = self.cars_scraper.scrape(url)
        search_id = str(uuid.uuid4())
        self.searchesRepository.insertCarsForSearch(search_id, name, url, cars)

    def analyze(
        self,
        search_id: str,
        weight_horsepower: float,
        weight_price: float,
        weight_mileage: float,
        weight_age: float,
        preferred_age: float,
        filter_by_manufacturer: str,
        filter_by_model: str,
    ) -> ScoredAndGroupedCars:
        cars = self.searchesRepository.getCarsForSearch(search_id)
        self.carsAnalyzer.set_cars(cars)
        scored_cars = self.carsAnalyzer.getScoredCars(
            weight_horsepower,
            weight_price,
            weight_mileage,
            weight_age,
            preferred_age,
            filter_by_manufacturer,
            filter_by_model,
        )
        grouped_cars = self.carsAnalyzer.get_grouped_cars()
        return ScoredAndGroupedCars(scored_cars, grouped_cars)

    def get_searches(self):
        return self.searchesRepository.getSearches()
