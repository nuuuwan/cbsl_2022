import os
import shutil
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from cbsl._constants import DIR_DATA, DIR_ROOT, URL
from cbsl._utils import log
from cbsl.frequency import FREQUNCY_CONFIG

TIME_WAIT_FOR_ERROR = 3
TIME_WAIT_FOR_PAGE1 = 10
MAX_PAGE1_RETRIES = 5
TIME_WAIT_ACTION = 0.5

ID_BUTTON_CLEAR_ALL = 'ContentPlaceHolder1_grdClearAll'
ID_BUTTON_NEXT = 'ContentPlaceHolder1_btnNext'
ID_BUTTON_BACK_PAGE1 = 'ContentPlaceHolder1_btnBack'
ID_BUTTON_BACK_PAGE2 = 'ContentPlaceHolder1_btnBack2'
ID_CHECKBOX_LIST_ALL_ITEMS = 'ContentPlaceHolder1_chkshowAll'
ID_SPAN_ERROR = 'ContentPlaceHolder1_lbl_errmsg'
ID_CHECKBOX_SELECT = 'chkSelect'
ID_BUTTON_ADD = 'add'
BROWSER_WIDTH, BROWSER_HEIGHT = 1000, 5000


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
    browser.set_window_size(BROWSER_WIDTH, BROWSER_HEIGHT)


def open_page1(browser, sub0, i_sub1, sub1, frequency_name):
    for i in range(0, MAX_PAGE1_RETRIES):
        try:
            r = open_page1_try(browser, sub0, i_sub1, sub1, frequency_name)
            return r
        except Exception as e:
            print(e)
            log.warning(f'open_page1_try: retry {i}')

    log.error(f'Failed after {MAX_PAGE1_RETRIES} retries')
    return False


def open_page1_try(browser, sub0, i_sub1, sub1, frequency_name):
    log.debug(
        f'Openning to page1 ({sub0}/{i_sub1}-{sub1}/{frequency_name})...')
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

    time_span = d['time_span']
    for i, elem_text_box in enumerate(elem_text_box_list):
        elem_text_box.clear()
        elem_text_box.send_keys(time_span[i])

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


def open_page2(browser):
    log.debug('Openning page2...')
    elem_selects = browser.find_elements_by_id(ID_CHECKBOX_SELECT)
    for elem_select in elem_selects:
        elem_select.click()
    time.sleep(TIME_WAIT_ACTION)

    elem_input_add = browser.find_element_by_id(ID_BUTTON_ADD)
    elem_input_add.click()
    time.sleep(TIME_WAIT_ACTION)

    elem_button_next = browser.find_element_by_id(ID_BUTTON_NEXT)
    elem_button_next.click()

    img_file = '/tmp/selenium.page2.png'
    browser.save_screenshot(img_file)
    log.debug(img_file)


def go_back_to_page0(browser):
    log.debug('Going back to page 0')
    elem_button_back = browser.find_element_by_id(ID_BUTTON_BACK_PAGE1)
    elem_button_back.click()
    time.sleep(TIME_WAIT_ACTION)


def go_back_to_page1(browser):
    log.debug('Going back page 1')
    elem_button_back = browser.find_element_by_id(ID_BUTTON_BACK_PAGE2)
    elem_button_back.click()
    time.sleep(TIME_WAIT_ACTION)
