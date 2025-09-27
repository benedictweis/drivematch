from dataclasses import dataclass
import random
import time
import datetime

from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import sys
import json


firefox_options = Options()
firefox_options.add_argument("--window-size=1920,1080")


@dataclass
class Car:
    providerId: str
    timestamp: int
    manufacturer: str
    model: str
    description: str
    price: int
    attributes: list[str]
    firstRegistration: int
    mileage: int
    horsePower: int
    fuelType: str
    advertisedSince: int
    isPrivateSeller: bool
    detailsURL: str
    imageURL: str


def scrape(url: str) -> list[Car]:
    soups = get_soups(url)
    cars = []
    for soup in soups:
        cars.extend(get_cars_from_soup(soup))
    cars = list({car.providerId: car for car in cars}.values())
    return cars


def get_soups(url: str) -> list[BeautifulSoup]:
    driver = webdriver.Firefox(options=firefox_options)
    driver.delete_all_cookies()
    driver.get(url)
    soups = []
    driver.implicitly_wait(10)
    consent_button = driver.find_element(
        By.CLASS_NAME,
        "mde-consent-accept-btn",
    )
    consent_button.click()
    while True:
        try:
            time.sleep(random.uniform(1, 2))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            soups.append(BeautifulSoup(driver.page_source, "html.parser"))
            time.sleep(random.uniform(1, 2))
            next_page = driver.find_element(
                By.CSS_SELECTOR,
                "button[aria-label='Weiter']",
            )
            next_page.click()
        except Exception:
            break
    driver.quit()
    return soups


def get_cars_from_soup(soup: BeautifulSoup) -> list[Car]:
    links = soup.select(
        "article > section > div > div > a[href^='/fahrzeuge/details.html?']",
    )
    cars = [parse_car_details(link) for link in links]
    return cars


def parse_car_details(link_element: Tag) -> Car:
    info_spans = link_element.find_all(
        lambda tag: tag.name == "span"
        and tag.get_text(strip=True) != "Gesponsert"
        and tag.get_text(strip=True) != "NEU",
    )
    infos = [get_text_from_tag(span) for span in info_spans]

    make_model = infos[0].split(" ")
    make = make_model[0]
    model = " ".join(make_model[1:])
    try:
        price = int(infos[1].replace("€", "").replace(".", "").strip())
        description = ""
    except ValueError:
        price = int(
            infos[2].replace("€", "").replace(".", "").replace("¹", "").strip(),
        )
        description = infos[1]

    online_since_div = link_element.find(
        lambda tag: tag.name == "div"
        and tag.get_text(strip=True).startswith("Inserat online seit"),
    )
    if online_since_div is None:
        advertised_since = datetime.datetime.now()
    else:
        online_since_text = get_text_from_tag(online_since_div).strip(
            "Inserat online seit "
        )
        advertised_since = datetime.datetime.strptime(
            online_since_text, "%d.%m.%Y, %H:%M"
        )

    additional_infos = get_text_from_tag(
        link_element.select_one("div > section > div > div"),
    ).split("•")
    additional_infos = [sanitize_string(info) for info in additional_infos]

    attributes = []
    first_registration = datetime.datetime.now()
    mileage = 0
    horse_power = 0
    fuel_type = ""

    for info in additional_infos:
        if info.startswith("EZ "):
            first_registration = datetime.datetime.strptime(info.split(" ")[1], "%m/%Y")
        elif "km" in info:
            mileage = int(info.split(" ")[0].replace(".", "").replace("km", ""))
        elif "PS" in info:
            horse_power = int(
                info.split("(")[1]
                .split(" ")[0]
                .replace("PS", "")
                .replace(")", "")
                .replace(".", ""),
            )
        elif info in ["Benzin", "Diesel", "Elektro", "Hybrid (Benzin/Elektro)"]:
            fuel_type = info
        else:
            attributes.append(info)

    car_id = link_element.get("href").split("id=")[1].split("&")[0]
    details_url = f"https://suchen.mobile.de{link_element.get('href')}"

    img = link_element.find(lambda tag: tag.name == "img")
    image_url = "" if img is None else img.get("src")

    last_div = link_element.find_all("div", recursive=False)[-1]
    first_div_inside_last = last_div.find("div")
    seller_info = get_text_from_tag(first_div_inside_last)

    private_seller = False

    if "Privatanbieter" in seller_info:
        private_seller = True

    return Car(
        providerId=car_id,
        timestamp=int(datetime.datetime.now().timestamp()),
        manufacturer=make,
        model=model,
        description=description,
        price=price,
        attributes=attributes,
        firstRegistration=int(first_registration.timestamp()),
        mileage=mileage,
        horsePower=horse_power,
        fuelType=fuel_type,
        advertisedSince=int(advertised_since.timestamp()),
        isPrivateSeller=private_seller,
        detailsURL=details_url,
        imageURL=image_url,
    )


def get_text_from_tag(input_tag: Tag) -> str:
    return sanitize_string(input_tag.get_text())


def sanitize_string(input_str: str) -> str:
    return input_str.replace("\xa0", " ").replace("\x00", "").strip()


if __name__ == "__main__":
    cars = scrape(sys.argv[1])
    cars_json = [car.__dict__ for car in cars]
    print(json.dumps(cars_json, default=str, indent=2))
