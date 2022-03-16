import math

from cbsl._utils import log
from cbsl.browser_common import save_screenshot
from cbsl.frequency import FREQUNCY_CONFIG
from cbsl.parsers import parse_step1, parse_step2, parse_step3
from cbsl.persistence import init, save_contents, save_results
from cbsl.scrapers import (go_back_to_step2, open_browser, open_step1,
                           open_step2, open_step3)

GROUP_SIZE = 30


def scrape_basic():
    browser = open_browser()
    open_step1(browser)
    idx12 = parse_step1(browser.page_source)
    save_contents(idx12, 'basic')
    return idx12


def scrape_sub2(sub1, i_sub2, sub2, frequency_name):
    browser = open_browser()
    open_step1(browser)
    save_screenshot(browser)

    elem_selects = open_step2(browser, sub1, i_sub2, sub2, frequency_name)
    save_screenshot(browser)

    if not elem_selects:
        browser.quit()
        return

    idx34 = parse_step2(browser.page_source)
    i_sub4_offset = 0
    for sub3 in idx34:
        sub4_list = list(idx34[sub3].values())
        n_sub4 = len(sub4_list)
        n_groups = math.ceil(n_sub4 / GROUP_SIZE)
        for i_group in range(0, n_groups):
            i_sub4_min = GROUP_SIZE * i_group
            i_sub4_max = min(i_sub4_min + GROUP_SIZE, n_sub4)

            open_step3(
                browser,
                i_sub4_offset +
                i_sub4_min,
                i_sub4_offset +
                i_sub4_max)
            save_screenshot(browser)

            [footnote_idx, results_idx] = parse_step3(
                browser.page_source,
            )
            save_results(
                sub1,
                sub2,
                sub3,
                frequency_name,
                i_group,
                results_idx,
                footnote_idx,
            )
            go_back_to_step2(browser)
        i_sub4_offset += n_sub4
        browser.quit()


def scrape_sub2_safe(sub1, i_sub2, sub2, frequency_name):
    try:
        scrape_sub2(sub1, i_sub2, sub2, frequency_name)
    except Exception as e:
        log.error(repr(e))
        log.error(f'Could not scrape: {sub1}/{sub2}')


def scrape_details(idx12):
    for sub1 in idx12:
        for i_sub2, sub2 in enumerate(list(idx12[sub1])):
            for frequency_name in FREQUNCY_CONFIG:
                scrape_sub2_safe(sub1, i_sub2, sub2, frequency_name)


def run():
    idx12 = scrape_basic()
    scrape_details(idx12)


if __name__ == '__main__':
    init()
    run()
