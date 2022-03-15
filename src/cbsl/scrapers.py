import os
import shutil
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from utils import jsonx

from cbsl._utils import log
from cbsl.frequency import FREQUNCY_CONFIG
from cbsl.parsers import parse_page0, parse_page1

URL = 'https://www.cbsl.lk/eresearch/'
DIR_ROOT = '/tmp/cbsl'
DIR_DATA = os.path.join(DIR_ROOT, 'data')

TIME_WAIT_FOR_ERROR = 3
TIME_WAIT_FOR_PAGE1 = 10
MAX_PAGE1_RETRIES = 5
TIME_WAIT_ACTION = 0.5

ID_BUTTON_CLEAR_ALL = 'ContentPlaceHolder1_grdClearAll'
ID_BUTTON_NEXT = 'ContentPlaceHolder1_btnNext'
ID_BUTTON_BACK = 'ContentPlaceHolder1_btnBack'
ID_CHECKBOX_LIST_ALL_ITEMS = 'ContentPlaceHolder1_chkshowAll'
ID_SPAN_ERROR = 'ContentPlaceHolder1_lbl_errmsg'


def init():
    shutil.rmtree(DIR_ROOT, ignore_errors=True)
    os.mkdir(DIR_ROOT)
    os.mkdir(DIR_DATA)


def open_browser():
    log.debug('Openning browser...')
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)
    return browser


def open_page0(browser):
    log.debug('Openning page0...')
    browser.get(URL)
    browser.set_window_size(1000, 12000)


def goto_page1(browser, sub0, i_sub1, sub1, frequency_name):
    for i in range(0, MAX_PAGE1_RETRIES):
        try:
            r = goto_page1_try(browser, sub0, i_sub1, sub1, frequency_name)
            return r
        except Exception as e:

            log.warning('Exception', e)
            log.warning(f'goto_page1_try: retry {i}')
    log.error(f'Failed after {MAX_PAGE1_RETRIES} retries')
    return False


def goto_page1_try(browser, sub0, i_sub1, sub1, frequency_name):
    log.debug(f'Going to page1 ({sub0}/{i_sub1}-{sub1}/{frequency_name})...')
    sub0_str = sub0.replace(' ', '')

    elem_button_clear_all = browser.find_element_by_id(ID_BUTTON_CLEAR_ALL)
    elem_button_clear_all.click()
    time.sleep(TIME_WAIT_ACTION)

    checkbox_id = f'ContentPlaceHolder1_grdSubjects_{sub0_str}' + \
        f'_chkIsSelect_{i_sub1}'
    elem_checkbox = browser.find_element_by_id(checkbox_id)
    elem_checkbox.click()
    time.sleep(TIME_WAIT_ACTION)

    select = Select(browser.find_element_by_tag_name('select'))
    html_value = frequency_name[0]
    select.select_by_value(html_value)
    time.sleep(TIME_WAIT_ACTION)

    d = FREQUNCY_CONFIG[frequency_name]
    elem_text_box_list = browser.find_elements_by_class_name(
        'form_txt_box')
    for elem_text_box in elem_text_box_list:
        elem_text_box.clear()
        elem_text_box.send_keys(d['dummy_value'])

    elem_button_next = browser.find_element_by_id(ID_BUTTON_NEXT)
    elem_button_next.click()

    try:
        WebDriverWait(
            browser,
            TIME_WAIT_FOR_ERROR,
        ).until(
            EC.presence_of_element_located(
                (By.ID, ID_SPAN_ERROR),
            ),
        )
        log.info(f'No elements for {sub0}/{sub1}/{frequency_name}')
        img_file = '/tmp/selenium.no_elements.png'
        browser.save_screenshot(img_file)
        log.debug(img_file)
        return False
    except TimeoutException:
        pass

    try:
        elem_checkbox_list_all_items = WebDriverWait(
            browser,
            TIME_WAIT_FOR_PAGE1,
        ).until(
            EC.presence_of_element_located(
                (By.ID, ID_CHECKBOX_LIST_ALL_ITEMS),
            ),
        )
    except TimeoutException:
        img_file = '/tmp/selenium.cannot_find_list_all.png'
        browser.save_screenshot(img_file)
        log.debug(img_file)
        raise Exception('Could not find ID_CHECKBOX_LIST_ALL_ITEMS')

    elem_checkbox_list_all_items.click()
    return True


def go_backto_page0(browser):
    img_file = '/tmp/selenium.back.png'
    browser.save_screenshot(img_file)
    log.debug(img_file)

    log.debug('Going back to page0')
    elem_button_back = browser.find_element_by_id(ID_BUTTON_BACK)
    elem_button_back.click()


def scrape_everything():
    browser = open_browser()
    open_page0(browser)
    idx = parse_page0(browser.page_source)

    for sub0 in idx:
        for i_sub1, sub1 in enumerate(list(idx[sub0])):
            for frequency_name in FREQUNCY_CONFIG:
                if goto_page1(browser, sub0, i_sub1, sub1, frequency_name):
                    idx1 = parse_page1(browser.page_source)
                    idx[sub0][sub1][frequency_name] = idx1
                    go_backto_page0(browser)
            break
        break

    data_file = os.path.join(DIR_DATA, 'contents.json')
    jsonx.write(data_file, idx)
    n_sub0 = len(idx)
    log.info(f'Wrote {n_sub0} sub0s to {data_file}')

    browser.quit()


if __name__ == '__main__':
    init()
    scrape_everything()
