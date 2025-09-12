from collections import defaultdict
import datetime
from collections.abc import Callable

import numpy as np
import scipy.optimize

from drivematch.types import (
    Car,
    GroupedCarsByManufacturerAndModel,
    RegressionFunctionType,
    ScoredCar,
)

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
        groups: dict[tuple[str, str], list[Car]] = defaultdict(list)
        for car in self.cars:
            groups[(car.manufacturer, car.model)].append(car)

        now = datetime.datetime.now()
        grouped_cars: list[GroupedCarsByManufacturerAndModel] = []

        for (manufacturer, model), group in groups.items():
            count = len(group)

            total_price = 0
            total_mileage = 0
            total_hp = 0
            total_age = 0
            total_ad_age = 0

            for car in group:
                total_price += car.price
                total_mileage += car.mileage
                total_hp += car.horse_power
                total_age += (now - car.first_registration).days
                total_ad_age += (now - car.advertised_since).days

            grouped_cars.append(
                GroupedCarsByManufacturerAndModel(
                    manufacturer=manufacturer,
                    model=model,
                    count=count,
                    average_price=total_price / count,
                    average_mileage=total_mileage / count,
                    average_horse_power=total_hp / count,
                    average_age=total_age / count,
                    average_advertisement_age=total_ad_age / count,
                    cars=group,
                )
            )

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

        now = datetime.datetime.now()

        self.min_age = min(
            (now - car.first_registration).days for car in self.cars
        )
        self.max_age = max(
            (now - car.first_registration).days for car in self.cars
        )
        self.min_advertisement_age = min(
            (now - car.advertised_since).days for car in self.cars
        )
        self.max_advertisement_age = max(
            (now - car.advertised_since).days for car in self.cars
        )

        scored_cars = [ScoredCar(car=car, score=self.score(car)) for car in self.cars]
        scored_cars = sorted(scored_cars, key=lambda x: x.score, reverse=True)
        if len(self.filter_by_manufacturers) > 0:
            scored_cars = [
                scored_car
                for scored_car in scored_cars
                if scored_car.car.manufacturer.lower()
                in [m.lower() for m in self.filter_by_manufacturers]
            ]
        if len(self.filter_by_models) > 0:
            scored_cars = [
                scored_car
                for scored_car in scored_cars
                if scored_car.car.model.lower()
                in [m.lower() for m in self.filter_by_models]
            ]
        return scored_cars

    def score(self, car: Car) -> float:
        now = datetime.datetime.now()

        age = (now - car.first_registration).days
        age = abs(age - self.preferred_age)

        advertisement_age = (now - car.advertised_since).days
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

    def get_regression_line(
        self,
        function_type: RegressionFunctionType,
    ) -> tuple[list[datetime.datetime], list[float]]:
        now = datetime.datetime.now()

        # Prepare data for regression
        x_data = np.array(
            [(now - car.first_registration).days / 365.25 for car in self.cars],
        )
        y_data = np.array([car.price for car in self.cars])

        if len(x_data) <= 1:
            return [], []

        depreciation_function = function_type.function

        params, _ = scipy.optimize.curve_fit(depreciation_function, x_data, y_data)

        # Generate points for the regression curve
        x_curve = np.linspace(x_data.min(), x_data.max(), 500)
        y_curve = np.array(
            [depreciation_function(x_point, *params) for x_point in x_curve]
        )
        x_curve = np.array(
            [now - datetime.timedelta(days=x * 365.25) for x in x_curve]
        )
        return x_curve, y_curve
