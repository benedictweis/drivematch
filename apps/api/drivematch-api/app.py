from fastapi import FastAPI
from pydantic import BaseModel

from drivematch.car import GroupedCarsByManufacturerAndModel, ScoredCar
from drivematch.core import create_default_drivematch_service

# https://suchen.mobile.de/fahrzeuge/search.html?c=EstateCar&clim=AUTOMATIC_CLIMATISATION_2_ZONES&cn=DE&con=USED&dam=false&fe=CARPLAY&fe=DIGITAL_COCKPIT&fe=ELECTRIC_ADJUSTABLE_SEATS&fe=SPORT_PACKAGE&fr=2021%3A&ft=DIESEL&ft=PETROL&gn=68766%2C+Hockenheim%2C+Baden-Württemberg&isSearchRequest=true&ll=49.3261824%2C8.5186845&ml=%3A50000&od=down&p=%3A52000&pw=147%3A&rd=100&ref=srpHead&s=Car&sb=doc&tr=AUTOMATIC_GEAR&vc=Car

drive_match_service = create_default_drivematch_service("./drivematch.db")

app = FastAPI()


class ScrapeRequest(BaseModel):
    name: str
    url: str


@app.post("/api/v2/scrape")
def scrape(scrapeRequest: ScrapeRequest):
    drive_match_service.scrape(scrapeRequest.name, scrapeRequest.url)


@app.get("/api/v2/scores")
def scores(
    search_id: str,
    weight_hp: float,
    weight_price: float,
    weight_mileage: float,
    weight_age: float,
    preferred_age: float,
    filter_by_manufacturer: str,
    filter_by_model: str,
) -> list[ScoredCar]:
    return drive_match_service.get_scores(
        search_id,
        weight_hp,
        weight_price,
        weight_mileage,
        weight_age,
        preferred_age,
        filter_by_manufacturer,
        filter_by_model,
    )


@app.get("/api/v2/groups")
def groups(search_id: str) -> list[GroupedCarsByManufacturerAndModel]:
    return drive_match_service.get_groups(search_id)


@app.get("/api/v2/searches")
def searches() -> list[Search]:
    return drive_match_service.get_searches()
