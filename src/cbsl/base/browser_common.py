from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils import timex

from cbsl._utils import log

TIME_WAIT_DEFAULT = 60
TIME_WAIT_DEFAULT_SAFE = 3


def scroll_down(browser):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def save_screenshot(browser):
    time_str = timex.get_time_id()
    png_file = f'/tmp/selenium.screenshot.{time_str}.png'
    browser.save_screenshot(png_file)
    log.debug(f'Saved {png_file}')


def find_element_by_id(browser, id, time_wait=TIME_WAIT_DEFAULT, do_log=True):
    log.debug(f'find_element_by_id: {id} ({time_wait}s)')
    return WebDriverWait(browser, time_wait).until(
        EC.presence_of_element_located((By.ID, id)),
    )


def find_elements_by_id(browser, id, time_wait=TIME_WAIT_DEFAULT):
    log.debug(f'find_elements_by_id: {id} ({time_wait}s)')
    find_element_by_id(browser, id, time_wait)
    return browser.find_elements(By.ID, id)


def find_element_by_class_name(
    browser, class_name, time_wait=TIME_WAIT_DEFAULT
):
    log.debug(f'find_element_by_class_name: {class_name} ({time_wait}s)')
    return WebDriverWait(browser, time_wait).until(
        EC.presence_of_element_located((By.CLASS_NAME, class_name)),
    )


def find_elements_by_class_name(
    browser, class_name, time_wait=TIME_WAIT_DEFAULT
):
    log.debug(f'find_elements_by_class_name: {class_name} ({time_wait}s)')
    find_element_by_class_name(browser, class_name, time_wait)
    return browser.find_elements(By.CLASS_NAME, class_name)


def find_element_by_tag_name(browser, tag_name, time_wait=TIME_WAIT_DEFAULT):
    log.debug(f'find_element_by_tag_name: {tag_name} ({time_wait}s)')
    return WebDriverWait(browser, time_wait).until(
        EC.presence_of_element_located((By.TAG_NAME, tag_name)),
    )


def find_element_by_id_safe(browser, id, time_wait=TIME_WAIT_DEFAULT_SAFE):
    log.debug(f'find_element_by_id_safe: {id} ({time_wait}s)')
    try:
        return find_element_by_id(browser, id, time_wait)
    except TimeoutException:
        return None
