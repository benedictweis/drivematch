import sqlite3

from abc import ABC, abstractmethod
from pydantic import BaseModel
from datetime import datetime

from drivematch.car import Car


class SearchInfo(BaseModel):
    id: str
    name: str
    url: str
    amount_of_cars: int
    date: str


class SearchesRepository(ABC):
    @abstractmethod
    def insert_cars_for_search(
        self, search_id: str, name: str, url: str, cars: list[Car]
    ):
        pass

    @abstractmethod
    def get_cars_for_search(self, search: str) -> list[Car]:
        pass

    @abstractmethod
    def get_searches(self) -> list[SearchInfo]:
        pass


class SQLiteSearchesRepository(SearchesRepository):
    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def insert_cars_for_search(
        self, search_id: str, name: str, url: str, cars: list[Car]
    ):
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            (
                "INSERT INTO searches (id, name, url, timestamp)"
                "VALUES (?, ?, ?, ?)"
            ),
            (search_id, name, url, current_datetime)
        )
        self.cursor.executemany(
            (
                "INSERT INTO cars (id, timestamp, manufacturer, model,"
                "description, price, attributes, firstRegistration, mileage,"
                "horsePower, fuelType, advertisedSince, privateSeller,"
                "detailsURL, imageURL)"
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            ),
            [
                (
                    car.id,
                    current_datetime,
                    car.manufacturer,
                    car.model,
                    car.description,
                    car.price,
                    ",".join(car.attributes),
                    car.first_registration.strftime("%Y-%m-%d"),
                    car.mileage,
                    car.horse_power,
                    car.fuel_type,
                    car.advertised_since.strftime("%Y-%m-%d %H:%M:%S"),
                    car.private_seller,
                    car.details_url,
                    car.image_url,
                )
                for car in cars
            ],
        )
        self.cursor.executemany(
            "INSERT INTO searches_cars (search_id, car_id) VALUES (?, ?)",
            [(search_id, car.id) for car in cars])
        self.connection.commit()

    def get_cars_for_search(self, search_id: str) -> list[Car]:
        self.cursor.execute("""
            SELECT timestamp
            FROM searches
            WHERE id = ?
        """, (search_id,))
        search_timestamp = self.cursor.fetchone()[0]
        if search_timestamp is None:
            raise ValueError(f"No search found with id {search_id}")
        self.cursor.execute("""
            SELECT cars.*
            FROM cars
            INNER JOIN searches_cars ON cars.id = searches_cars.car_id
            WHERE searches_cars.search_id = ? AND cars.timestamp = ?
        """, (search_id, search_timestamp))
        rows = self.cursor.fetchall()
        cars = []
        for row in rows:
            car = Car(
                id=row[0],
                manufacturer=row[2],
                model=row[3],
                description=row[4],
                price=row[5],
                attributes=row[6].split(","),
                first_registration=datetime.strptime(row[7], "%Y-%m-%d"),
                mileage=row[8],
                horse_power=row[9],
                fuel_type=row[10],
                advertised_since=datetime.strptime(row[11], "%Y-%m-%d %H:%M:%S"),
                private_seller=bool(row[12]),
                details_url=row[13],
                image_url=row[14]
            )
            cars.append(car)
        return cars

    def get_searches(self) -> list[SearchInfo]:
        self.cursor.execute("SELECT * FROM searches")
        rows = self.cursor.fetchall()
        searches = []
        for row in rows:
            search = SearchInfo(
                id=row[0],
                name=row[1],
                url=row[2],
                amount_of_cars=len(self.get_cars_for_search(row[0])),
                date=row[3]
            )
            searches.append(search)
        self.connection.commit()
        return searches


if __name__ == "__main__":
    db_path = "drivematch.db"
    repository = SQLiteSearchesRepository(db_path)

    search_id = "search123456"
    name = "Example Search"
    url = "http://example.com"
    cars = [
        Car(
            id="car1",
            manufacturer="Toyota",
            model="Corolla",
            description="A reliable car",
            price=20000,
            attributes=["automatic", "sedan"],
            first_registration=datetime.now(),
            mileage=15000,
            horse_power=150,
            fuel_type="Petrol",
            advertised_since=datetime.now(),
            private_seller=False,
            details_url="http://example.com/car1",
            image_url="http://example.com/car1.jpg"
        )
    ]

    repository.insert_cars_for_search(search_id, name, url, cars)

    retrieved_cars = repository.get_cars_for_search(search_id)
    print("Retrieved Cars:")
    print(retrieved_cars)

    searches = repository.get_searches()
    print("Searches:")
    print(searches)
