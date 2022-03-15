from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

TIME_WAIT_DEFAULT = 10


def scroll_down(browser):

    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def find_element_by_id(browser, id, time_wait=TIME_WAIT_DEFAULT):
    return WebDriverWait(browser, time_wait).until(
        EC.presence_of_element_located((By.ID, id)),
    )


def find_element_by_class_name(
        browser,
        class_name,
        time_wait=TIME_WAIT_DEFAULT):
    return WebDriverWait(browser, time_wait).until(
        EC.presence_of_element_located((By.CLASS_NAME, class_name)),
    )


def find_element_by_tag_name(
        browser,
        tag_name,
        time_wait=TIME_WAIT_DEFAULT):
    return WebDriverWait(browser, time_wait).until(
        EC.presence_of_element_located((By.TAG_NAME, tag_name)),
    )


def find_element_by_id_safe(browser, id, time_wait=TIME_WAIT_DEFAULT):
    try:
        return find_element_by_id(browser, id, time_wait)
    except TimeoutException:
        return None
