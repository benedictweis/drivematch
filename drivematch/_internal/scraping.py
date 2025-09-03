import random
import time
from abc import ABC, abstractmethod
from datetime import datetime

from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

from drivematch.types import Car

firefox_options = Options()
firefox_options.add_argument("--window-size=1920,1080")
# firefox_options.add_argument("--headless")


def get_text_from_tag(input_tag: Tag) -> str:
    return sanitize_string(input_tag.get_text())


def sanitize_string(input_str: str) -> str:
    return input_str.replace("\xa0", " ").replace("\x00", "").strip()


class CarsScraper(ABC):
    @abstractmethod
    def scrape(self, url: str) -> list[Car]:
        pass


class MobileDeScraper(CarsScraper):
    def scrape(self, url: str) -> list[Car]:
        soups = self.__get_soups(url)
        cars = []
        for soup in soups:
            cars.extend(self.__get_cars_from_soup(soup))
        cars = list({car.id: car for car in cars}.values())
        return cars

    def __get_soups(self, url: str) -> list[BeautifulSoup]:
        driver = webdriver.Firefox(options=firefox_options)
        driver.delete_all_cookies()
        driver.get(url)
        soups = []
        # nav_element = driver.find_element(
        #    By.CSS_SELECTOR, "nav[aria-label='Weitere Angebote']"
        # )
        # second_to_last_li = nav_element.find_elements(
        #    By.CSS_SELECTOR, "ul > li"
        # )[-2]
        # _ = float(second_to_last_li.text.strip())
        time.sleep(random.uniform(1, 2))
        consent_button = driver.find_element(
            By.CLASS_NAME,
            "mde-consent-accept-btn",
        )
        consent_button.click()
        time.sleep(random.uniform(1, 2))
        while True:
            try:
                soups.append(BeautifulSoup(driver.page_source, "html.parser"))
                next_page = driver.find_element(
                    By.CSS_SELECTOR,
                    "button[aria-label='Weiter']",
                )
                next_page.click()
                time.sleep(random.uniform(3, 5))
            except Exception:
                break
        driver.quit()
        return soups

    def __get_cars_from_soup(self, soup: BeautifulSoup) -> list[Car]:
        links = soup.select(
            "article > section > div > div > a[href^='/fahrzeuge/details.html?']",
        )
        cars = [self.__parse_car_details(link) for link in links]
        return cars

    def __parse_car_details(self, link_element: Tag) -> Car:
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
            advertised_since = datetime.now()
        else:
            online_since_text = get_text_from_tag(online_since_div).strip(
                "Inserat online seit "
            )
            advertised_since = datetime.strptime(online_since_text, "%d.%m.%Y, %H:%M")

        additional_infos = get_text_from_tag(
            link_element.select_one("div > section > div > div"),
        ).split("•")
        additional_infos = [sanitize_string(info) for info in additional_infos]

        attributes = []
        first_registration = datetime.now()
        mileage = 0
        horse_power = 0
        fuel_type = ""

        for info in additional_infos:
            if info.startswith("EZ "):
                first_registration = datetime.strptime(info.split(" ")[1], "%m/%Y")
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
            id=car_id,
            timestamp=datetime.now(),
            manufacturer=make,
            model=model,
            description=description,
            price=price,
            attributes=attributes,
            first_registration=first_registration,
            mileage=mileage,
            horse_power=horse_power,
            fuel_type=fuel_type,
            advertised_since=advertised_since,
            private_seller=private_seller,
            details_url=details_url,
            image_url=image_url,
        )
