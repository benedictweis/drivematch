import logging
import uuid

from drivematch._internal.analysis import CarsAnalyzer
from drivematch._internal.db import Search, SearchesRepository, SQLiteSearchesRepository
from drivematch._internal.scraping import CarsScraper, MobileDeScraper
from drivematch.types import GroupedCarsByManufacturerAndModel, ScoredCar

logger = logging.getLogger(__name__)


class DriveMatchService:
    def __init__(
        self,
        searches_repository: SearchesRepository,
        cars_scraper: CarsScraper,
        cars_analyzer: CarsAnalyzer,
    ) -> None:
        self.searches_repository = searches_repository
        self.cars_scraper = cars_scraper
        self.cars_analyzer = cars_analyzer

    def scrape(self, name: str, url: str) -> None:
        logger.info("Scraping with name=%s and url=%s", name, url)
        cars = self.cars_scraper.scrape(url)
        search_id = str(uuid.uuid4())
        self.searches_repository.insert_cars_for_search(
            search_id,
            name,
            url,
            cars,
        )

    def get_scores(  # noqa: PLR0913
        self,
        search_id: str,
        weight_horsepower: float,
        weight_price: float,
        weight_mileage: float,
        weight_age: float,
        preferred_age: float,
        weight_advertisement_age: float,
        preferred_advertisement_age: float,
        filter_by_manufacturers: list[str],
        filter_by_models: list[str],
    ) -> list[ScoredCar]:
        logger.info("Getting scores for search search_id=%s", search_id)
        cars = self.searches_repository.get_cars_for_search(search_id)
        self.cars_analyzer.set_cars(cars)
        self.cars_analyzer.set_weights_and_filters(
            weight_horsepower,
            weight_price,
            weight_mileage,
            weight_age,
            preferred_age,
            weight_advertisement_age,
            preferred_advertisement_age,
            filter_by_manufacturers,
            filter_by_models,
        )
        return self.cars_analyzer.get_scored_cars()

    def get_groups(
        self,
        search_id: str,
    ) -> list[GroupedCarsByManufacturerAndModel]:
        logger.info("Getting groups for search search_id=%s", search_id)
        cars = self.searches_repository.get_cars_for_search(search_id)
        self.cars_analyzer.set_cars(cars)
        return self.cars_analyzer.get_grouped_cars()

    def get_searches(self) -> list[Search]:
        logger.info("Getting searches")
        return self.searches_repository.get_searches()


def create_default_drivematch_service(db_path: str) -> DriveMatchService:
    return DriveMatchService(
        SQLiteSearchesRepository(db_path),
        MobileDeScraper(),
        CarsAnalyzer(),
    )
