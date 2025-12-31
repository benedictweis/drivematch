import util
import json
from typing import Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


FIREFOX_OPTIONS = Options()
FIREFOX_OPTIONS.add_argument("--window-size=1920,1080")


def get_info_from_search_strings(input_json: str) -> list[dict[str, Any]]:
    entries = json.loads(input_json)
    driver = webdriver.Firefox(options=FIREFOX_OPTIONS)
    driver.delete_all_cookies()

    infos = []
    for entry in entries:
        car_hash = entry["car_hash"]
        url = entry["url"]
        info = get_info_from_search_string(driver, url)
        infos.append({"car_hash": car_hash, "url": url, "data": info})

    driver.quit()
    return infos


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
