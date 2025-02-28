from datetime import datetime

import msgspec

class Car(msgspec.Struct):
    id: str
    manufacturer: str
    model: str
    description: str
    price: int
    attributes: list[str]
    firstRegistration: datetime
    mileage: int
    horsePower: int
    fuelType: str
    detailsURL: str
    imageURL: str


class ScoredCar(msgspec.Struct):
    car: Car
    score: float

class GroupedCarsByManufacturerAndModel(msgspec.Struct):
    manufacturer: str
    model: str
    count: int
    averagePrice: float
    averageMileage: float
    averageHorsePower: float
    averageAge: float
    