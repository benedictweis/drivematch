from datetime import datetime

import msgspec


class Car(msgspec.Struct):
    id: str
    manufacturer: str
    model: str
    description: str
    price: int
    attributes: list[str]
    first_registration: datetime
    mileage: int
    horse_power: int
    fuel_type: str
    details_url: str
    image_url: str


class ScoredCar(msgspec.Struct):
    car: Car
    score: float


class GroupedCarsByManufacturerAndModel(msgspec.Struct):
    manufacturer: str
    model: str
    count: int
    average_price: float
    average_mileage: float
    average_horse_power: float
    average_age: float


class ScoredAndGroupedCars(msgspec.Struct):
    scored_cars: list[ScoredCar]
    grouped_cars: list[GroupedCarsByManufacturerAndModel]
