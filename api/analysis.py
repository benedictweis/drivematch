from typing import Callable
from datetime import datetime

from api.car import Car, GroupedCarsByManufacturerAndModel, ScoredCar


def group_by[T](
    elements: list[T],
    equals: Callable[[T, T], bool]
) -> list[list[T]]:
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
        self.set_cars(cars)

    def set_cars(self, cars: list[Car]):
        self.cars = cars

    def get_grouped_cars(self) -> list[GroupedCarsByManufacturerAndModel]:
        grouped_cars = list[GroupedCarsByManufacturerAndModel]()
        for group in group_by(
            self.cars,
            lambda car1, car2: car1.manufacturer == car2.manufacturer
            and car1.model == car2.model
        ):
            average_age = sum(
                (datetime.now() - car.firstRegistration).days for car in group
            ) / len(group)
            grouped_cars_entry = GroupedCarsByManufacturerAndModel(
                group[0].manufacturer,
                group[0].model,
                len(group),
                sum(car.price for car in group) / len(group),
                sum(car.mileage for car in group) / len(group),
                sum(car.horsePower for car in group) / len(group),
                average_age
            )
            grouped_cars.append(grouped_cars_entry)
        grouped_cars.sort(key=lambda x: x.count, reverse=True)
        return grouped_cars

    def set_weights_and_filters(
        self,
        weight_hp: float,
        weight_price: float,
        weight_mileage: float,
        weight_age: float,
        preferred_age: float,
        filter_by_manufacturer: str,
        filter_by_model: str
    ):
        self.weight_hp = weight_hp
        self.weight_price = weight_price
        self.weight_mileage = weight_mileage
        self.weight_age = weight_age
        self.preferred_age = preferred_age
        self.filter_by_manufacturer = filter_by_manufacturer
        self.filter_by_model = filter_by_model

    def get_scored_cars(self) -> list[ScoredCar]:
        self.min_hp = min(car.horsePower for car in self.cars)
        self.max_hp = max(car.horsePower for car in self.cars)
        self.min_price = min(car.price for car in self.cars)
        self.max_price = max(car.price for car in self.cars)
        self.min_mileage = min(car.mileage for car in self.cars)
        self.max_mileage = max(car.mileage for car in self.cars)
        self.min_age = min(
            (datetime.now() - car.firstRegistration).days
            for car in self.cars
        )
        self.max_age = max(
            (datetime.now() - car.firstRegistration).days
            for car in self.cars
        )

        scored_cars = [ScoredCar(car, self.score(car)) for car in self.cars]
        scored_cars = sorted(scored_cars, key=lambda x: x.score, reverse=True)
        if self.filter_by_manufacturer != '':
            scored_cars = [
                car for car in scored_cars
                if car.car.manufacturer == self.filter_by_manufacturer
            ]
        if self.filter_by_model != '':
            scored_cars = [
                car for car in scored_cars
                if car.car.model == self.filter_by_model
            ]
        return scored_cars

    def score(self, car: Car) -> float:
        age = (datetime.now() - car.firstRegistration).days
        age = abs(age - self.preferred_age)

        normalized_hp = normalize(car.horsePower, self.min_hp, self.max_hp)
        normalized_price = normalize(car.price, self.min_price, self.max_price)
        normalized_mileage = normalize(
            car.mileage, self.min_mileage, self.max_mileage
        )
        normalized_age = normalize(age, self.min_age, self.max_age)

        return (
            (normalized_hp * self.weight_hp) +
            (normalized_price * self.weight_price) +
            (normalized_mileage * self.weight_mileage) +
            (normalized_age * self.weight_age)
        )
