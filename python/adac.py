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

ADAC_DE_CAR_DETAILS_LOOKUP_PREFIX = "https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle"

def get_info_from_search_strings(input_json: str) -> list[dict[str, Any]]:
    entries = json.loads(input_json)
    driver = webdriver.Firefox(options=FIREFOX_OPTIONS)
    driver.delete_all_cookies()

    infos = []
    for entry in entries:
        try:
            urls = []
            hsn = ""
            tsn = ""
            lookup_hsn_tsn_str = ""
            if "url" in entry and entry["url"]:
                urls.append(entry["url"])
            elif "hsn" in entry and entry["hsn"] and "tsn" in entry and entry["tsn"]:
                if "lookup_hsn_tsn" in entry and entry["lookup_hsn_tsn"] is True:
                    lookup_string = lookup_hsn_tsn(driver, entry["hsn"], entry["tsn"])
                    if lookup_string:
                        search_keyword = f"site:{ADAC_DE_CAR_DETAILS_LOOKUP_PREFIX} {lookup_string}"
                    else:
                        continue
                else:
                    search_keyword = f"site:{ADAC_DE_CAR_DETAILS_LOOKUP_PREFIX} HSN {entry['hsn']} TSN {entry['tsn']}"

                google_urls = perform_google_search(driver, search_keyword)
                urls.extend(google_urls)
            else:
                continue

            # Deduplicate URLs
            urls = list(set(urls))

            if len(urls) == 0:
                continue

            for url in urls:
                try:
                    info = get_info_from_search_string(driver, url)
                    infos.append({"hsn": hsn, "tsn": tsn,"url": url, "data": info})
                except:
                    continue
        except:
            break

    driver.quit()
    return infos

def lookup_hsn_tsn(driver, hsn: str, tsn: str) -> str | None:
    driver.get(
        f"http://www.hsn-tsn.de/hsn-tsn.php?{hsn}-{tsn}"
    )

    util.wait_for_network_idle(driver)

    try:
        model_element = driver.find_element(By.CSS_SELECTOR, 'span[property="model"]')
        year_element = driver.find_element(By.CSS_SELECTOR, 'small[property="vehicleModelDate"]')
        return f"{model_element.text.strip()} {year_element.get_attribute("content").strip()}"
    except:
        return None


def perform_google_search(driver, query: str) -> list[str]:
    driver.get(
        f"https://www.google.com/search?q={query}",
    )

    util.wait_for_network_idle(driver)

    try:
        driver.find_element(By.ID, "captcha-form")

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "a[href^='https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modell']",
                )
            )
        )
    except:
        pass

    all_link_elements = driver.find_elements(
        By.CSS_SELECTOR,
        "a[href^='https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modell']",
    )

    return [link.get_attribute("href") for link in all_link_elements]


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
