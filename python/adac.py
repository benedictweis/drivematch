import util
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


FIREFOX_OPTIONS = Options()
FIREFOX_OPTIONS.add_argument("--window-size=1920,1080")


def get_info_from_search_strings(input_json: str) -> list[dict[str, str]]:
    search_strings = json.loads(input_json)
    driver = webdriver.Firefox(options=FIREFOX_OPTIONS)
    driver.delete_all_cookies()

    infos = []
    for search_string in search_strings:
        try:
            info = get_info_from_search_string(driver, search_string)
            infos.append(info)
        except Exception:
            pass

    driver.quit()
    return infos


def get_info_from_search_string(driver, search_string: str) -> dict[str, str]:
    url = ""
    if search_string.startswith("https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle"):
        url = search_string
    else:
        driver.get(
            f"https://www.google.com/search?q=site:https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle {search_string}"
        )
        util.wait_for_network_idle(driver)

        first_link = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "a[href^='https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modell']",
                )
            )
        )
        url = first_link.get_attribute("href") + "#technische-daten"

    driver.get(url)

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
