import datetime

from pydantic import BaseModel


class Search(BaseModel):
    id: str
    name: str
    url: str
    timestamp: datetime.datetime
    amount_of_cars: int


class Car(BaseModel):
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
    average_advertisement_age: float
    cars: list[Car]
