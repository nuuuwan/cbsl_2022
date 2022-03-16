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
    idx = parse_step1(browser.page_source)
    save_contents(idx, 'basic')
    return idx


def scrape_sub2(sub1, i_sub2, sub2, frequency_name):
    browser = open_browser()
    open_step1(browser)
    save_screenshot(browser)

    elem_selects = open_step2(browser, sub1, i_sub2, sub2, frequency_name)
    save_screenshot(browser)

    if not elem_selects:
        browser.quit()
        return

    parse_step2(browser.page_source)
    n_elem_selects = len(elem_selects)
    n_groups = math.ceil(n_elem_selects / GROUP_SIZE)
    for i_group in range(0, n_groups):
        i_min = GROUP_SIZE * i_group
        i_max = min(i_min + GROUP_SIZE, n_elem_selects)
        open_step3(browser, i_min, i_max)
        save_screenshot(browser)

        [footnote_idx, results_idx] = parse_step3(
            browser.page_source,
        )
        save_results(
            sub1,
            sub2,
            frequency_name,
            i_group,
            results_idx,
            footnote_idx,
        )
        go_back_to_step2(browser)
    browser.quit()


def scrape_details(idx):
    for sub1 in idx:
        for i_sub2, sub2 in enumerate(list(idx[sub1])):
            for frequency_name in FREQUNCY_CONFIG:
                try:
                    scrape_sub2(sub1, i_sub2, sub2, frequency_name)
                except Exception:
                    log.error(f'Could not scrape: {sub1}/{sub2}')


def run():
    idx = scrape_basic()
    scrape_details(idx)


if __name__ == '__main__':
    init()
    run()
