import time

JS_GET_NETWORK_ACTIVITY = "return window.performance.getEntriesByType('resource').length;"
NETWORK_ACTIVITY_CHECK_INTERVAL = 1

def wait_for_network_idle(driver):
    old_network_activity = driver.execute_script(JS_GET_NETWORK_ACTIVITY)
    while True:
        time.sleep(NETWORK_ACTIVITY_CHECK_INTERVAL)
        new_network_activity = driver.execute_script(JS_GET_NETWORK_ACTIVITY)
        if old_network_activity == new_network_activity:
            break
        old_network_activity = new_network_activity
