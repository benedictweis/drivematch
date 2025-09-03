import datetime

import pytest

from drivematch._internal.analysis import CarsAnalyzer
from drivematch.types import Car


@pytest.fixture
def car1() -> Car:
    return Car(
        id="test_car_1",
        timestamp=datetime.datetime.now(),
        manufacturer="BMW",
        model="M3",
        description="BMW M3 test car",
        price=70000,
        mileage=15000,
        horse_power=450,
        fuel_type="Petrol",
        first_registration=datetime.datetime(2020, 1, 1),
        advertised_since=datetime.datetime.now(),
        private_seller=False,
        details_url="https://example.com/car1",
        image_url="https://example.com/car1.jpg",
        attributes=["a", "b"],
    )


@pytest.fixture
def car2() -> Car:
    return Car(
        id="test_car_2",
        timestamp=datetime.datetime.now(),
        manufacturer="BMW",
        model="M3",
        description="another BMW M3 test car",
        price=75000,
        mileage=30000,
        horse_power=450,
        fuel_type="Petrol",
        first_registration=datetime.datetime(2020, 1, 1),
        advertised_since=datetime.datetime.now(),
        private_seller=False,
        details_url="https://example.com/car1",
        image_url="https://example.com/car1.jpg",
        attributes=["a", "b"],
    )


@pytest.mark.unit
def test_should_group_cars_with_same_manufacturer_and_model(
    car1: Car, car2: Car
) -> None:
    analyzer = CarsAnalyzer()
    analyzer.set_cars([car1, car2])
    assert analyzer.cars == [car1, car2]

    grouped_cars = analyzer.get_grouped_cars()
    assert len(grouped_cars) == 1
    assert grouped_cars[0].manufacturer == "BMW"
    assert grouped_cars[0].model == "M3"
    assert grouped_cars[0].count == 2
    assert grouped_cars[0].average_price == 72500
    assert grouped_cars[0].average_mileage == 22500
    assert grouped_cars[0].average_horse_power == 450
    assert grouped_cars[0].average_advertisement_age == 0
    assert grouped_cars[0].cars == [car1, car2]


def test_should_score_cars_according_to_weights_set(car1: Car, car2: Car) -> None:
    analyzer = CarsAnalyzer()
    analyzer.set_cars([car1, car2])
    assert analyzer.cars == [car1, car2]

    analyzer.set_weights_and_filters(
        weight_hp=1.0,
        weight_price=-1.0,
        weight_mileage=-1.0,
        weight_age=-1.0,
        preferred_age=0,
        weight_advertisement_age=0,
        preferred_advertisement_age=0,
        filter_by_manufacturers=[],
        filter_by_models=[],
    )
    scored_cars = analyzer.get_scored_cars()
    assert len(scored_cars) == 2
    assert scored_cars[0].car == car1
    assert scored_cars[1].car == car2
    assert scored_cars[0].score > scored_cars[1].score
