from collections.abc import Callable
from datetime import datetime

from drivematch.types import Car, GroupedCarsByManufacturerAndModel, ScoredCar


def group_by[T](
    elements: list[T],
    equals: Callable[[T, T], bool],
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


def normalize(
    value: float, min_value: float, max_value: float, epsilon: float = 1e-10
) -> float:
    if min_value == max_value:
        return 1.0
    return (value - min_value + epsilon) / (max_value - min_value + epsilon)


class CarsAnalyzer:
    def __init__(self, cars: list[Car] = []) -> None:
        self.set_cars(cars)

    def set_cars(self, cars: list[Car]) -> None:
        self.cars = cars

    def get_grouped_cars(self) -> list[GroupedCarsByManufacturerAndModel]:
        grouped_cars = list[GroupedCarsByManufacturerAndModel]()
        for group in group_by(
            self.cars,
            lambda car1, car2: car1.manufacturer == car2.manufacturer
            and car1.model == car2.model,
        ):
            average_age = sum(
                (datetime.now() - car.first_registration).days for car in group
            ) / len(group)
            average_advertisement_age = sum(
                (datetime.now() - car.advertised_since).days for car in group
            ) / len(group)
            grouped_cars_entry = GroupedCarsByManufacturerAndModel(
                manufacturer=group[0].manufacturer,
                model=group[0].model,
                count=len(group),
                average_price=sum(car.price for car in group) / len(group),
                average_mileage=sum(car.mileage for car in group) / len(group),
                average_horse_power=(
                    sum(car.horse_power for car in group) / len(group)
                ),
                average_age=average_age,
                average_advertisement_age=average_advertisement_age,
                cars=group,
            )
            grouped_cars.append(grouped_cars_entry)
        grouped_cars.sort(key=lambda x: x.count, reverse=True)
        return grouped_cars

    def set_weights_and_filters(  # noqa: PLR0913
        self,
        weight_hp: float,
        weight_price: float,
        weight_mileage: float,
        weight_age: float,
        preferred_age: float,
        weight_advertisement_age: float,
        preferred_advertisement_age: float,
        filter_by_manufacturers: list[str],
        filter_by_models: list[str],
    ) -> None:
        self.weight_hp = weight_hp
        self.weight_price = weight_price
        self.weight_mileage = weight_mileage
        self.weight_age = weight_age
        self.preferred_age = preferred_age
        self.weight_advertisement_age = weight_advertisement_age
        self.preferred_advertisement_age = preferred_advertisement_age
        self.filter_by_manufacturers = filter_by_manufacturers
        self.filter_by_models = filter_by_models

    def get_scored_cars(self) -> list[ScoredCar]:
        if self.cars is None or len(self.cars) == 0:
            return []
        self.min_hp = min(car.horse_power for car in self.cars)
        self.max_hp = max(car.horse_power for car in self.cars)
        self.min_price = min(car.price for car in self.cars)
        self.max_price = max(car.price for car in self.cars)
        self.min_mileage = min(car.mileage for car in self.cars)
        self.max_mileage = max(car.mileage for car in self.cars)
        self.min_age = min(
            (datetime.now() - car.first_registration).days for car in self.cars
        )
        self.max_age = max(
            (datetime.now() - car.first_registration).days for car in self.cars
        )
        self.min_advertisement_age = min(
            (datetime.now() - car.advertised_since).days for car in self.cars
        )
        self.max_advertisement_age = max(
            (datetime.now() - car.advertised_since).days for car in self.cars
        )

        scored_cars = [ScoredCar(car=car, score=self.score(car)) for car in self.cars]
        scored_cars = sorted(scored_cars, key=lambda x: x.score, reverse=True)
        if len(self.filter_by_manufacturers) > 0:
            scored_cars = [
                scored_car
                for scored_car in scored_cars
                if scored_car.car.manufacturer in self.filter_by_manufacturers
                and scored_car.car.model in self.filter_by_models
            ]
        return scored_cars

    def score(self, car: Car) -> float:
        age = (datetime.now() - car.first_registration).days
        age = abs(age - self.preferred_age)

        advertisement_age = (datetime.now() - car.advertised_since).days
        advertisement_age = abs(
            advertisement_age - self.preferred_advertisement_age,
        )

        normalized_hp = normalize(car.horse_power, self.min_hp, self.max_hp)
        normalized_price = normalize(car.price, self.min_price, self.max_price)
        normalized_mileage = normalize(
            car.mileage,
            self.min_mileage,
            self.max_mileage,
        )
        normalized_age = normalize(age, self.min_age, self.max_age)
        normalized_advertisement_age = normalize(
            advertisement_age,
            self.min_advertisement_age,
            self.max_advertisement_age,
        )

        return (
            (normalized_hp * self.weight_hp)
            + (normalized_price * self.weight_price)
            + (normalized_mileage * self.weight_mileage)
            + (normalized_age * self.weight_age)
            + (normalized_advertisement_age * self.weight_advertisement_age)
        )
