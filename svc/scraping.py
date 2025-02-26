from datetime import datetime
import time    

from bs4 import BeautifulSoup, Tag
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from abc import ABC, abstractmethod

from svc.types import Car

def getSoupFromURL(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36'})
    return BeautifulSoup(response.content, 'html.parser')

def getTextFromTag(input: Tag) -> str:
    return sanitizeString(input.get_text())

def sanitizeString(input: str) -> str:
    return input.replace("\xa0", " ").replace("\x00", "").strip()

class CarsScraper(ABC):
    @abstractmethod
    def scrape(self, url: str) -> list[Car]:
        pass

class MobileDeScraper(CarsScraper): 
    def scrape(self, url: str) -> list[Car]:
        pageURLs = self.getPageURLs(url)
        cars = list[Car]()
        currentPage = 0
        for pageURL in pageURLs:
            print(f"{round(currentPage/len(pageURLs)*100)}%")
            currentPage += 1
            cars.extend(self.getCarsFromPage(pageURL))
            time.sleep(1)
        print("100%")
        cars = list({car.id: car for car in cars}.values())
        return cars

    def getPageURLs(self, url: str) -> list[str]:
        soup = getSoupFromURL(url)

        pages = self.amountOfPages(soup)
        print(f"Found {pages} pages in search")

        pageURLs = [self.setPageNumber(url, pageNumber) for pageNumber in range(1, pages + 1)]

        return pageURLs

    def setPageNumber(self, url: str, pageNumber: int) -> str:
        urlParts = urlparse(url)
        query = parse_qs(urlParts.query)
        query["pageNumber"] = [str(pageNumber)]
        new_query = urlencode(query, doseq=True)
        urlParts = urlParts._replace(query=new_query)
        return urlunparse(urlParts)

    def amountOfPages(self, page: Tag) -> int:
        nav = page.find("nav", attrs={"aria-label": "Weitere Angebote"})
        li_elements = nav.find_all("li")
        second_last_li = li_elements[-2]
        return int(getTextFromTag(second_last_li))

    def getCarsFromPage(self, url) -> list[Car]:
        soup = getSoupFromURL(url)
        links = soup.select("article > section > div > div > a[href^='/fahrzeuge/details.html?']")
        cars = [self.parseCarDetails(link) for link in links]
        return cars

    def parseCarDetails(self, linkElement: Tag) -> Car:
        infoSpans = linkElement.find_all(lambda tag: tag.name == "span" and tag.getText(strip=True) != "Gesponsert" and tag.getText(strip=True) != "NEU")
        infos = [getTextFromTag(span) for span in infoSpans]

        makeModel = infos[0].split(" ")
        make = makeModel[0]
        model = " ".join(makeModel[1:])
        try:
            price = int(infos[1].replace("€", "").replace(".", "").strip())
            description = ""
        except ValueError:
            price = int(infos[2].replace("€", "").replace(".", "").strip())
            description = infos[1]

        additionalInfos = getTextFromTag(linkElement.select_one("div > section > div > div")).split("•")
        additionalInfos = [sanitizeString(info) for info in additionalInfos]

        attributes = []
        firstRegistration = datetime.now()
        mileage = 0
        horsePower = 0
        fuelType = ""

        for info in additionalInfos:
            if info.startswith("EZ "):
                firstRegistration = datetime.strptime(info.split(" ")[1], "%m/%Y")
            elif "km" in info:
                mileage = int(info.split(" ")[0].replace(".", "").replace("km", ""))
            elif "PS" in info:
                horsePower = int(info.split("(")[1].split(" ")[0].replace("PS", "").replace(")", ""))
            elif info in ["Benzin", "Diesel", "Elektro", "Hybrid (Benzin/Elektro)"]:
                fuelType = info
            else:
                attributes.append(info)

        id = linkElement.get("href").split("id=")[1].split("&")[0]
        detailsURL = f'https://suchen.mobile.de{linkElement.get("href")}'     
        
        img = linkElement.find(lambda tag: tag.name == "img")
        if img is None:
            imageURL = ""
        else:   
            imageURL = img.get("src")
        
        return Car(id, make, model, description, price, attributes, firstRegistration, mileage, horsePower, fuelType, detailsURL, imageURL)
