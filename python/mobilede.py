import util

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

CONSENT_BUTTON_CLASS_NAME = "mde-consent-accept-btn"
NEXT_PAGE_BUTTON_CSS_SELECTOR = "button[aria-label='Weiter']"
JS_GET_CAR_ITEMS = (
    "return window.__INITIAL_STATE__.search.srp.data.searchResults.items;"
)

FIREFOX_OPTIONS = Options()
FIREFOX_OPTIONS.add_argument("--window-size=1920,1080")


def get_cars_from_url(url: str) -> list[str]:
    driver = webdriver.Firefox(options=FIREFOX_OPTIONS)
    driver.delete_all_cookies()
    driver.implicitly_wait(10)
    driver.get(url)

    consent_button = driver.find_element(
        By.CLASS_NAME,
        CONSENT_BUTTON_CLASS_NAME,
    )
    consent_button.click()

    cars = []
    while True:
        util.wait_for_network_idle(driver)

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

            next_page = driver.find_element(
                By.CSS_SELECTOR, NEXT_PAGE_BUTTON_CSS_SELECTOR
            )
            next_page.click()
        except Exception:
            break

    driver.quit()

    cars = [car for car in cars if "id" in car]
    unique_cars = {car["id"]: car for car in cars}.values()
    return list(unique_cars)
