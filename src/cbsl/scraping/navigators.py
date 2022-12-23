from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

from cbsl._constants import URL
from cbsl._utils import log
from cbsl.base.browser_common import (find_element_by_class_name,
                                      find_element_by_id,
                                      find_element_by_id_safe,
                                      find_element_by_tag_name,
                                      find_elements_by_class_name,
                                      find_elements_by_id, scroll_down)
from cbsl.core.frequency import FREQUENCY_CONFIG

TIME_WAIT_FOR_ERROR = 3
TIME_WAIT_FOR_PAGE1 = 10
MAX_PAGE1_RETRIES = 5
TIME_WAIT_ACTION = 0.5

CLASS_TXT_BOX = 'form_txt_box'
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
    browser = webdriver.Chrome(
        ChromeDriverManager().install(), options=options
    )
    return browser


def open_step1(browser):
    log.debug('Openning step1...')
    browser.get(URL)
    browser.set_window_size(BROWSER_WIDTH, BROWSER_HEIGHT)
    find_element_by_class_name(browser, CLASS_TABLE0)


def open_step2(browser, sub1, i_sub2, sub2, frequency_name):
    log.debug(
        f'Openning to step2 ({sub1}/{i_sub2}-{sub2}/{frequency_name})...'
    )

    find_element_by_id(browser, ID_BUTTON_CLEAR_ALL).click()

    sub1_str = sub1.replace('-', ' ').title().replace(' ', '')
    checkbox_id = (
        'ContentPlaceHolder1_grdSubjects_'
        + f'{sub1_str}_chkIsSelect_{i_sub2}'
    )
    find_element_by_id(browser, checkbox_id).click()

    select = Select(find_element_by_tag_name(browser, 'select'))
    select.select_by_value(frequency_name[0].upper())

    elem_text_box_list = find_elements_by_class_name(browser, CLASS_TXT_BOX)

    d = FREQUENCY_CONFIG[frequency_name]
    time_span = d['time_span']
    for i, elem_text_box in enumerate(elem_text_box_list):
        elem_text_box.clear()
        elem_text_box.send_keys(time_span[i])

    scroll_down(browser)
    find_element_by_id(browser, ID_BUTTON_NEXT).click()

    elem = find_element_by_id_safe(browser, ID_SPAN_ERROR)
    if elem:
        log.info(f'No elements for {sub1}/{sub2}/{frequency_name}')
        return False

    find_element_by_id(browser, ID_CHECKBOX_LIST_ALL_ITEMS).click()
    return find_elements_by_id(browser, ID_CHECKBOX_SELECT)


def open_step3(browser, i_min, i_max):
    log.debug(f'Openning step3 ({i_min} to {i_max})...')

    chk = find_element_by_id(browser, ID_CHECKBOX_LIST_ALL_ITEMS)
    if not chk.is_selected():
        chk.click()

    has_del = find_element_by_id_safe(browser, ID_IMG_DEL)
    if has_del:
        for elem_del in find_elements_by_id(
            browser,
            ID_IMG_DEL,
        ):
            elem_del.click()

    elem_selects = find_elements_by_id(browser, ID_CHECKBOX_SELECT)

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


def go_back_to_step1(browser):
    log.debug('Going back step 1')
    find_element_by_id(browser, ID_BUTTON_BACK_PAGE1).click()


def go_back_to_step2(browser):
    log.debug('Going back step 2')
    find_element_by_id(browser, ID_BUTTON_BACK_PAGE2).click()
