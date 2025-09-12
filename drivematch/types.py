import datetime
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from drivematch._internal import regression_functions


@dataclass
class Search:
    id: str
    name: str
    url: str
    timestamp: datetime.datetime
    amount_of_cars: int


@dataclass
class Car:
    id: str
    timestamp: datetime.datetime
    manufacturer: str
    model: str
    description: str
    price: int
    attributes: list[str]
    first_registration: datetime.datetime
    mileage: int
    horse_power: int
    fuel_type: str
    advertised_since: datetime.datetime
    private_seller: bool
    details_url: str
    image_url: str


@dataclass
class ScoredCar:
    car: Car
    score: float


@dataclass
class GroupedCarsByManufacturerAndModel:
    manufacturer: str
    model: str
    count: int
    average_price: float
    average_mileage: float
    average_horse_power: float
    average_age: float
    average_advertisement_age: float
    cars: list[Car]


class RegressionFunctionType(Enum):
    LINEAR = ("Linear", regression_functions.linear_depreciation)
    EXPONENTIAL = (
        "Exponential",
        regression_functions.exponential_depreciation,
    )
    POWER_LAW = ("Power Law", regression_functions.power_law_depreciation)
    LOGARITHMIC = (
        "Logarithmic",
        regression_functions.logarithmic_depreciation,
    )
    POLYNOMIAL_2 = (
        "Polynomial 2",
        regression_functions.polynomial_2_depreciation,
    )
    POLYNOMIAL_3 = (
        "Polynomial 3",
        regression_functions.polynomial_3_depreciation,
    )
    POLYNOMIAL_4 = (
        "Polynomial 4",
        regression_functions.polynomial_4_depreciation,
    )

    function: Callable

    def __new__(cls, value: str, function: Callable) -> object:
        obj = object.__new__(cls)
        obj._value_ = value
        obj.function = function
        return obj
