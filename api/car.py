from datetime import datetime
from pydantic import BaseModel


class Car(BaseModel):
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


class ScoredCar(BaseModel):
    car: Car
    score: float


class GroupedCarsByManufacturerAndModel(BaseModel):
    manufacturer: str
    model: str
    count: int
    average_price: float
    average_mileage: float
    average_horse_power: float
    average_age: float


class ScoredAndGroupedCars(BaseModel):
    scored_cars: list[ScoredCar]
    grouped_cars: list[GroupedCarsByManufacturerAndModel]
