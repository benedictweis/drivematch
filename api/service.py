
from api.analysis import CarsAnalyzer
from api.scraping import CarsScraper
from api.types import ScoredAndGroupedCars


class DriveMatchService():
    def __init__(self, carsScraper: CarsScraper, carsAnalyzer: CarsAnalyzer):
        self.carsScraper = carsScraper
        self.carsAnalyzer = carsAnalyzer
    
    def scrapeAndAnalyze(self, url: str, weightHorsepower: float, weightPrice: float, weightMileage: float, weightAge: float, filterByManufacturer: str, filterByModel: str) -> ScoredAndGroupedCars:
        cars = self.carsScraper.scrape(url)
        self.carsAnalyzer.setCars(cars)
        scoredCars = self.carsAnalyzer.getScoredCars(weightHorsepower, weightPrice, weightMileage, weightAge, filterByManufacturer, filterByModel)
        groupedCars = self.carsAnalyzer.getGroupedCars()
        return ScoredAndGroupedCars(scoredCars, groupedCars)