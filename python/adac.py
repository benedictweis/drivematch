import util
import json
from typing import Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidSessionIdException


FIREFOX_OPTIONS = Options()
FIREFOX_OPTIONS.add_argument("--window-size=1920,1080")


def get_info_from_search_strings(input_json: str) -> list[dict[str, Any]]:
    entries = json.loads(input_json)
    driver = webdriver.Firefox(options=FIREFOX_OPTIONS)
    driver.delete_all_cookies()

    infos = []
    for entry in entries:
        try:
            url = ""
            search_keyword = ""
            if "url" in entry and entry["url"]:
                url = entry["url"]
            elif "search_keyword" in entry and entry["search_keyword"]:
                search_keyword = entry["search_keyword"]
                url = perform_google_search(driver, search_keyword)
                if not url:
                    continue
            else:
                continue

            info = get_info_from_search_string(driver, url)
            infos.append({"search_keyword": search_keyword, "url": url, "data": info})
        except:
            break

    driver.quit()
    return infos


def perform_google_search(driver, query: str) -> str | None:
    driver.get(
        f"https://www.google.com/search?q={query}",
    )

    util.wait_for_network_idle(driver)

    try:
        driver.find_element(By.ID, "captcha-form")
        wait_time = 20
    except:
        wait_time = 1

    try:
        first_link = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "a[href^='https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modell']",
                )
            )
        )
    except:
        return None

    return first_link.get_attribute("href")


def get_info_from_search_string(driver, url: str) -> dict[str, str]:
    driver.get(url + "#technische-daten")

    util.wait_for_network_idle(driver)

    details: dict[str, str] = {}
    details["link"] = url

    image_element = driver.find_element(
        By.CSS_SELECTOR, "div[title='Technische Daten'] img"
    )
    image_url = image_element.get_attribute("src")
    details["image_url"] = image_url

    tables = driver.find_elements(By.CSS_SELECTOR, "div[title] table")
    for table in tables:
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) == 2:
                key = cells[0].text.strip()
                value = cells[1].text.strip()
                if key and value:
                    details[key] = value

    return details
