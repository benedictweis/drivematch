import datetime

import pytest

from drivematch._internal.db import SQLiteSearchesRepository
from drivematch.types import Car


@pytest.mark.unit
def test_should_analyze_cars_data() -> None:
    repository = SQLiteSearchesRepository(":memory:")

    now = datetime.datetime.now().replace(microsecond=0)
    today = now.date()

    search_id = "search123456"
    name = "Example Search"
    url = "http://example.com"
    cars = [
        Car(
            id="car1",
            timestamp=now,
            manufacturer="Toyota",
            model="Corolla",
            description="A reliable car",
            price=20000,
            attributes=["automatic", "sedan"],
            first_registration=today,
            mileage=15000,
            horse_power=150,
            fuel_type="Petrol",
            advertised_since=now,
            private_seller=False,
            details_url="http://example.com/car1",
            image_url="http://example.com/car1.jpg",
        ),
    ]

    repository.insert_cars_for_search(search_id, name, url, cars)

    retrieved_cars = repository.get_cars_for_search(search_id)
    assert retrieved_cars == cars

    searches = repository.get_searches()
    assert len(searches) == 1
    assert searches[0].id == search_id
    assert searches[0].name == name
    assert searches[0].url == url
    assert searches[0].amount_of_cars == len(cars)
