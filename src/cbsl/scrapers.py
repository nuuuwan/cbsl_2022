
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

from cbsl._constants import URL
from cbsl._utils import log
from cbsl.browser_common import (find_element_by_class_name,
                                 find_element_by_id, find_element_by_id_safe,
                                 find_element_by_tag_name, save_screenshot,
                                 scroll_down)
from cbsl.frequency import FREQUNCY_CONFIG

TIME_WAIT_FOR_ERROR = 3
TIME_WAIT_FOR_PAGE1 = 10
MAX_PAGE1_RETRIES = 5
TIME_WAIT_ACTION = 0.5

CLASS_TABLE0 = 'subjectgrid'
ID_TABLE_PAGE1_SEARCH_LIST = 'ContentPlaceHolder1_grdSearchList'
ID_TABLE_PAGE2_FOOTNOTES = 'ContentPlaceHolder1_grdFootNotes'
ID_TABLE_PAGE2_RESULTS = 'ContentPlaceHolder1_grdResult'
ID_BUTTON_CLEAR_ALL = 'ContentPlaceHolder1_grdClearAll'
ID_BUTTON_NEXT = 'ContentPlaceHolder1_btnNext'
ID_BUTTON_BACK_PAGE1 = 'ContentPlaceHolder1_btnBack'
ID_BUTTON_BACK_PAGE2 = 'ContentPlaceHolder1_btnBack2'
ID_CHECKBOX_LIST_ALL_ITEMS = 'ContentPlaceHolder1_chkshowAll'
ID_SPAN_ERROR = 'ContentPlaceHolder1_lbl_errmsg'
ID_CHECKBOX_SELECT = 'chkSelect'
ID_BUTTON_ADD = 'add'
ID_IMG_DEL = 'del'
BROWSER_WIDTH, BROWSER_HEIGHT = 1000, 12000


def open_browser():
    log.debug('Openning browser...')
    options = Options()
    options.headless = True
    browser = webdriver.Chrome(options=options)
    return browser


def open_page0(browser):
    log.debug('Openning page0...')
    browser.get(URL)
    browser.set_window_size(BROWSER_WIDTH, BROWSER_HEIGHT)
    find_element_by_class_name(browser, CLASS_TABLE0)


def open_page1(browser, sub0, i_sub1, sub1, frequency_name):
    log.debug(
        f'Openning to page1 ({sub0}/{i_sub1}-{sub1}/{frequency_name})...')

    find_element_by_class_name(browser, CLASS_TABLE0)
    find_element_by_id(browser, ID_BUTTON_CLEAR_ALL).click()

    sub0_str = sub0.replace(' ', '')
    checkbox_id = 'ContentPlaceHolder1_grdSubjects_'  \
        + f'{sub0_str}_chkIsSelect_{i_sub1}'
    find_element_by_id(browser, checkbox_id).click()

    select = Select(find_element_by_tag_name(browser, 'select'))
    select.select_by_value(frequency_name[0])

    d = FREQUNCY_CONFIG[frequency_name]
    elem_text_box_list = browser.find_elements_by_class_name(
        'form_txt_box')
    time_span = d['time_span']
    for i, elem_text_box in enumerate(elem_text_box_list):
        elem_text_box.clear()
        elem_text_box.send_keys(time_span[i])

    scroll_down(browser)
    find_element_by_id(browser, ID_BUTTON_NEXT).click()

    elem = find_element_by_id_safe(browser, ID_SPAN_ERROR)
    if elem:
        log.info(f'No elements for {sub0}/{sub1}/{frequency_name}')
        return False

    find_element_by_id(browser, ID_CHECKBOX_LIST_ALL_ITEMS).click()
    find_element_by_id(browser, ID_CHECKBOX_SELECT)
    return browser.find_elements_by_id(ID_CHECKBOX_SELECT)


def open_page2(browser, i_min, i_max):
    log.debug(f'Openning page2 ({i_min} to {i_max})...')

    chk = find_element_by_id(browser, ID_CHECKBOX_LIST_ALL_ITEMS)
    if not chk.is_selected():
        chk.click()

    for elem_del in browser.find_elements_by_id(ID_IMG_DEL):
        elem_del.click()

    elem_selects = browser.find_elements_by_id(ID_CHECKBOX_SELECT)
    save_screenshot(browser)
    n_elem_selects = len(elem_selects)
    log.debug(f'Found {n_elem_selects} elem_selects')
    for i in range(0, n_elem_selects):
        elem_select = elem_selects[i]
        elem_select.is_selected()
        if i_min <= i < i_max:
            if not elem_select.is_selected():
                elem_select.click()

    find_element_by_id(browser, ID_BUTTON_ADD).click()

    scroll_down(browser)
    find_element_by_id(browser, ID_BUTTON_NEXT).click()

    find_element_by_id(browser, ID_TABLE_PAGE2_RESULTS)
    find_element_by_id(browser, ID_TABLE_PAGE2_FOOTNOTES)


def go_back_to_page0(browser):
    log.debug('Going back page 0')
    find_element_by_id(browser, ID_BUTTON_BACK_PAGE1).click()


def go_back_to_page1(browser):
    log.debug('Going back page 1')
    find_element_by_id(browser, ID_BUTTON_BACK_PAGE2).click()
