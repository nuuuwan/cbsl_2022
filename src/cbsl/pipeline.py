import math
import os
import shutil

from utils import jsonx, tsv

from cbsl._constants import DIR_DATA, DIR_ROOT
from cbsl._utils import log
from cbsl.frequency import FREQUNCY_CONFIG
from cbsl.parsers import parse_page0, parse_page1, parse_page2
from cbsl.scrapers import (go_back_to_page1, open_browser, open_page0,
                           open_page1, open_page2)

GROUP_SIZE = 30


def init():
    shutil.rmtree(DIR_ROOT, ignore_errors=True)
    os.mkdir(DIR_ROOT)
    os.mkdir(DIR_DATA)


def save_results(
        sub0,
        sub1,
        frequency_name,
        i_group,
        results_idx,
        footnote_idx):
    dir = os.path.join(
        DIR_DATA,
        sub0,
        sub1,
    ).replace(' ', '-').lower()

    if not os.path.exists(dir):
        os.system(f'mkdir -p "{dir}"')

    data_list = []
    metadata_idx = {}
    for sub3, d in results_idx.items():
        data_list.append(
            {
                'sub3': sub3,
            } | dict(reversed(d['results'].items()))
        )
        metadata_idx[sub3] = {
            'sub3': sub3,
            'unit': d['unit'],
            'scale': d['scale'],
        } | footnote_idx.get(sub3, {})

    frequency_name_str = frequency_name.replace(' ', '-').lower()
    file_prefix = f'{frequency_name_str}-{i_group:03d}'

    tsv_file = os.path.join(dir, f'{file_prefix}.tsv')
    tsv.write(tsv_file, data_list)
    n_rows = len(data_list)
    n_cols = len(data_list[0])
    log.info(f'Wrote {tsv_file} ({n_rows}x{n_cols})')

    metadata_file = os.path.join(dir, f'{file_prefix}.metadata.json')
    jsonx.write(metadata_file, metadata_idx)
    log.info(f'Wrote {metadata_file}')


def save_contents(idx, prefix):
    data_file = os.path.join(DIR_DATA, f'contents.{prefix}.json')
    jsonx.write(data_file, idx)
    n_sub0 = len(idx)
    log.info(f'Wrote {n_sub0} sub0s to {data_file}')


def scrape_basic():
    browser = open_browser()
    open_page0(browser)
    idx = parse_page0(browser.page_source)
    save_contents(idx, 'basic')
    return idx


def scrape_sub1(sub0, i_sub1, sub1, frequency_name):
    browser = open_browser()
    open_page0(browser)

    elem_selects = open_page1(browser, sub0, i_sub1, sub1, frequency_name)
    if not elem_selects:
        browser.quit()
        return

    parse_page1(browser.page_source)
    n_elem_selects = len(elem_selects)
    n_groups = math.ceil(n_elem_selects / GROUP_SIZE)
    for i_group in range(0, n_groups):
        i_min = GROUP_SIZE * i_group
        i_max = min(i_min + GROUP_SIZE, n_elem_selects)
        open_page2(browser, i_min, i_max)

        [footnote_idx, results_idx] = parse_page2(
            browser.page_source,
        )
        save_results(
            sub0,
            sub1,
            frequency_name,
            i_group,
            results_idx,
            footnote_idx,
        )
        go_back_to_page1(browser)
    browser.quit()


def scrape_details(idx):
    for sub0 in idx:
        for i_sub1, sub1 in enumerate(list(idx[sub0])):
            for frequency_name in FREQUNCY_CONFIG:
                try:
                    scrape_sub1(sub0, i_sub1, sub1, frequency_name)
                except Exception:
                    log.error(f'Could not scrape: {sub0}/{sub1}')
            break


def run():
    idx = scrape_basic()
    scrape_details(idx)


if __name__ == '__main__':
    init()
    run()
