import time
import sys
import base64
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


CONSENT_BUTTON_CLASS_NAME = "mde-consent-accept-btn"
NEXT_PAGE_BUTTON_CSS_SELECTOR = "button[aria-label='Weiter']"
JS_GET_NETWORK_ACTIVITY = (
    "return window.performance.getEntriesByType('resource').length;"
)
JS_GET_CAR_ITEMS = (
    "return window.__INITIAL_STATE__.search.srp.data.searchResults.items;"
)

FIREFOX_OPTIONS = Options()
FIREFOX_OPTIONS.add_argument("--window-size=1920,1080")


def getPagesHTMLFromURL(url: str) -> list[str]:
    driver = webdriver.Firefox(options=FIREFOX_OPTIONS)
    driver.delete_all_cookies()
    driver.implicitly_wait(10)
    driver.get(url)

    consentButton = driver.find_element(
        By.CLASS_NAME,
        CONSENT_BUTTON_CLASS_NAME,
    )
    consentButton.click()

    cars = []
    while True:
        while True:
            old_network_activity = driver.execute_script(JS_GET_NETWORK_ACTIVITY)
            time.sleep(2)
            new_network_activity = driver.execute_script(JS_GET_NETWORK_ACTIVITY)
            if old_network_activity == new_network_activity:
                break

        try:
            try:
                items = driver.execute_script(JS_GET_CAR_ITEMS)
                for car in items:
                    if "items" in car and car["items"] is not None:
                        cars.extend(car["items"])
                    else:
                        cars.append(car)
            except Exception:
                continue

            nextPage = driver.find_element(
                By.CSS_SELECTOR, NEXT_PAGE_BUTTON_CSS_SELECTOR
            )
            nextPage.click()
        except Exception:
            break

    driver.quit()
    return cars


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    baseURL = base64.b64decode(sys.argv[1]).decode("utf-8")

    cars = getPagesHTMLFromURL(baseURL)
    cars = [car for car in cars if "id" in car]
    unique_cars = {car["id"]: car for car in cars}.values()
    cars = list(unique_cars)

    print(json.dumps(cars, indent=2, ensure_ascii=False))
