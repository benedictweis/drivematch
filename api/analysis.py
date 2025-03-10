from typing import Callable
from datetime import datetime

from api.types import Car, GroupedCarsByManufacturerAndModel, ScoredCar
    
def groupBy[T](elements: list[T], equals: Callable[[T, T], bool]) -> list[list[T]]:
    grouped = []
    for element in elements:
        found = False
        for group in grouped:
            if equals(element, group[0]):
                group.append(element)
                found = True
                break
        if not found:
            grouped.append([element])
    return grouped

def normalize(value, min_value, max_value, epsilon=1e-10):
    if min_value == max_value:
        return 1.0
    return (value - min_value + epsilon) / (max_value - min_value + epsilon)

class CarsAnalyzer:
    def __init__(self, cars: list[Car] = []):
        self.setCars(cars)
        
    def setCars(self, cars: list[Car]):
        self.cars = cars
    
    def getGroupedCars(self) -> list[GroupedCarsByManufacturerAndModel]:
        groupedCars = list[GroupedCarsByManufacturerAndModel]()
        for group in groupBy(self.cars, lambda car1, car2: car1.manufacturer == car2.manufacturer and car1.model == car2.model):
            average_age = sum((datetime.now() - car.firstRegistration).days for car in group) / len(group)
            groupedCarsEntry = GroupedCarsByManufacturerAndModel(
                group[0].manufacturer, 
                group[0].model, 
                len(group), 
                sum(car.price for car in group) / len(group), 
                sum(car.mileage for car in group) / len(group), 
                sum(car.horsePower for car in group) / len(group),
                average_age
            )
            groupedCars.append(groupedCarsEntry)
        groupedCars.sort(key=lambda x: x.count, reverse=True)
        return groupedCars
    
    def getScoredCars(self, weight_hp: float = 1.0, weight_price: float = -1.0, weight_mileage: float = -1.0, weight_age: float = -1.0, filterByManufacturer = '', filterByModel = '') -> list[ScoredCar]:
        min_hp = min(car.horsePower for car in self.cars)
        max_hp = max(car.horsePower for car in self.cars)
        min_price = min(car.price for car in self.cars)
        max_price = max(car.price for car in self.cars)
        min_mileage = min(car.mileage for car in self.cars)
        max_mileage = max(car.mileage for car in self.cars)
        min_age = min((datetime.now() - car.firstRegistration).days for car in self.cars)
        max_age = max((datetime.now() - car.firstRegistration).days for car in self.cars)
        
        scoredCars = [ScoredCar(car, self.score(car, min_hp=min_hp, max_hp=max_hp, min_price=min_price, max_price=max_price, min_mileage=min_mileage, max_mileage=max_mileage, min_age=min_age, max_age=max_age, weight_hp=weight_hp, weight_price=weight_price, weight_mileage=weight_mileage, weight_age=weight_age)) for car in self.cars]
        scoredCars = sorted(scoredCars, key=lambda x: x.score, reverse=True)
        if filterByManufacturer != '':
            scoredCars = [car for car in scoredCars if car.car.manufacturer == filterByManufacturer]
        if filterByModel != '':
            scoredCars = [car for car in scoredCars if car.car.model == filterByModel]
        return scoredCars

    def score(self, car: Car, min_hp: float, max_hp: float, min_price: float, max_price: float,
              min_mileage: float, max_mileage: float, min_age: float, max_age: float,
              weight_hp: float = 1.0, weight_price: float = -1.0, weight_mileage: float = -1.0, weight_age: float = -1.0) -> float:
        age = (datetime.now() - car.firstRegistration).days

        normalized_hp = normalize(car.horsePower, min_hp, max_hp)
        normalized_price = normalize(car.price, min_price, max_price)
        normalized_mileage = normalize(car.mileage, min_mileage, max_mileage)
        normalized_age = normalize(age, min_age, max_age)

        return (normalized_hp * weight_hp) + (normalized_price * weight_price) + (normalized_mileage * weight_mileage) + (normalized_age * weight_age)
