import pytest

from drivematch._internal.scraping import MobileDeScraper


@pytest.mark.component
def test_mobile_de_scraper_initialization() -> None:
    scraper = MobileDeScraper()

    cars = scraper.scrape(
        "https://suchen.mobile.de/fahrzeuge/search.html?asl=true&cn=DE&dam=false&gn=68766%2C+Hockenheim%2C+Baden-Württemberg&isSearchRequest=true&ll=49.3261824%2C8.5186845&ms=135%3B3%3B%3B&rd=100&ref=quickSearch&s=Car&vc=Car"
    )

    assert cars is not None
    assert len(cars) > 0
