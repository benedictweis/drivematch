from datetime import datetime
import random
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from abc import ABC, abstractmethod

from api.car import Car

user_agents = [
    """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,
     like Gecko) Chrome/92.0.4515.159 Safari/537.36""",
    """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,
     like Gecko) Chrome/91.0.4472.124 Safari/537.36""",
    """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,
     like Gecko) Chrome/90.0.4430.212 Safari/537.36""",
    """Mozilla/5.0 (iPhone14,3; U; CPU iPhone OS 15_0 like Mac OS X)
     AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/19A346
      Safari/602.1"""
]

firefox_options = Options()
random_user_agent = random.choice(user_agents)
firefox_options.add_argument(f"--user-agent={random_user_agent}")


def get_soup_from_url(url):
    driver = webdriver.Firefox(options=firefox_options)
    driver.get(url)
    time.sleep(5)
    source = driver.page_source
    driver.quit()
    return BeautifulSoup(source, 'html.parser')


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
        page_urls = self.get_page_urls(url)
        cars = []
        current_page = 0
        for page_url in page_urls:
            print(f"{round(current_page / len(page_urls) * 100)}%")
            current_page += 1
            cars.extend(self.get_cars_from_page(page_url))
            time.sleep(1)
        print("100%")
        cars = list({car.id: car for car in cars}.values())
        return cars

    def get_page_urls(self, url: str) -> list[str]:
        soup = get_soup_from_url(url)

        pages = self.amount_of_pages(soup)
        print(f"Found {pages} pages in search")

        page_urls = [
            self.set_page_number(url, page_number)
            for page_number in range(1, pages + 1)
        ]

        return page_urls

    def set_page_number(self, url: str, page_number: int) -> str:
        url_parts = urlparse(url)
        query = parse_qs(url_parts.query)
        query["pageNumber"] = [str(page_number)]
        new_query = urlencode(query, doseq=True)
        url_parts = url_parts._replace(query=new_query)
        return urlunparse(url_parts)

    def amount_of_pages(self, page: Tag) -> int:
        nav = page.find("nav", attrs={"aria-label": "Weitere Angebote"})
        li_elements = nav.find_all("li")
        second_last_li = li_elements[-2]
        return int(get_text_from_tag(second_last_li))

    def get_cars_from_page(self, url) -> list[Car]:
        soup = get_soup_from_url(url)
        links = soup.select(
            """article > section > div > div
            > a[href^='/fahrzeuge/details.html?']"""
        )
        cars = [self.parse_car_details(link) for link in links]
        return cars

    def parse_car_details(self, link_element: Tag) -> Car:
        info_spans = link_element.find_all(
            lambda tag: tag.name == "span"
            and tag.get_text(strip=True) != "Gesponsert"
            and tag.get_text(strip=True) != "NEU"
        )
        infos = [get_text_from_tag(span) for span in info_spans]
        print(infos)

        make_model = infos[0].split(" ")
        make = make_model[0]
        model = " ".join(make_model[1:])
        try:
            price = int(infos[1].replace("€", "").replace(".", "").strip())
            description = ""
        except ValueError:
            price = int(
                infos[2].replace("€", "")
                .replace(".", "")
                .replace("¹", "")
                .strip()
            )
            description = infos[1]

        additional_infos = get_text_from_tag(
            link_element.select_one("div > section > div > div")
        ).split("•")
        additional_infos = [sanitize_string(info) for info in additional_infos]

        attributes = []
        first_registration = datetime.now()
        mileage = 0
        horse_power = 0
        fuel_type = ""

        for info in additional_infos:
            if info.startswith("EZ "):
                first_registration = datetime.strptime(info.
                                                       split(" ")[1], "%m/%Y")
            elif "km" in info:
                mileage = int(info
                              .split(" ")[0]
                              .replace(".", "")
                              .replace("km", ""))
            elif "PS" in info:
                horse_power = int(
                    info.split("(")[1]
                    .split(" ")[0]
                    .replace("PS", "")
                    .replace(")", "")
                )
            elif info in ["Benzin",
                          "Diesel",
                          "Elektro",
                          "Hybrid (Benzin/Elektro)"]:
                fuel_type = info
            else:
                attributes.append(info)

        car_id = link_element.get("href").split("id=")[1].split("&")[0]
        details_url = f'https://suchen.mobile.de{link_element.get("href")}'

        img = link_element.find(lambda tag: tag.name == "img")
        if img is None:
            image_url = ""
        else:
            image_url = img.get("src")

        return Car(
            car_id,
            make,
            model,
            description,
            price,
            attributes,
            first_registration,
            mileage,
            horse_power,
            fuel_type,
            details_url,
            image_url,
        )
