import os
import shutil
import math

from utils import jsonx, tsv

from cbsl._constants import DIR_DATA, DIR_ROOT
from cbsl._utils import log
from cbsl.frequency import FREQUNCY_CONFIG
from cbsl.parsers import parse_page0, parse_page1, parse_page2
from cbsl.scrapers import (go_back_to_page0, go_back_to_page1, open_browser,
                           open_page0, open_page1, open_page2)

GROUP_SIZE = 4

def init():
    shutil.rmtree(DIR_ROOT, ignore_errors=True)
    os.mkdir(DIR_ROOT)
    os.mkdir(DIR_DATA)


def save_table(sub0, sub1, frequency_name, i_group, results_idx):
    dir = os.path.join(
        DIR_DATA,
        sub0,
        sub1,
    ).replace(' ', '-').lower()

    if not os.path.exists(dir):
        os.system(f'mkdir -p "{dir}"')

    data_list = []
    for sub3, d in results_idx.items():
        data_list.append(
            {
                'sub3': sub3,
                'unit': d['unit'],
                'scale': d['scale'],
            } | d['results']
        )
    frequency_name_str = frequency_name.replace(' ', '-').lower()
    tsv_file = os.path.join(dir, f'{frequency_name_str}-{i_group:03d}.tsv')
    tsv.write(tsv_file, data_list)
    n_rows = len(data_list)
    n_cols = len(data_list[0])
    log.info(f'Wrote {n_rows}x{n_cols} table to {tsv_file}')


def save_contents(idx, prefix):
    data_file = os.path.join(DIR_DATA, f'contents.{prefix}.json')
    jsonx.write(data_file, idx)
    n_sub0 = len(idx)
    log.info(f'Wrote {n_sub0} sub0s to {data_file}')


def run():
    browser = open_browser()
    open_page0(browser)
    idx = parse_page0(browser.page_source)

    save_contents(idx, 'basic')

    for sub0 in idx:
        for i_sub1, sub1 in enumerate(list(idx[sub0])):
            # if i_sub1 == 0:
            #     continue
            for frequency_name in FREQUNCY_CONFIG:
                elem_selects = open_page1(
                    browser, sub0, i_sub1, sub1, frequency_name)
                if elem_selects:
                    idx1 = parse_page1(browser.page_source)

                    n_elem_selects = len(elem_selects)
                    n_groups = math.ceil(n_elem_selects / GROUP_SIZE)
                    for i_group in range(0, n_groups):
                        i_min = GROUP_SIZE * i_group
                        i_max = min(i_min + GROUP_SIZE, n_elem_selects)
                        open_page2(browser, i_min, i_max)

                        [footnote_idx, results_idx] = parse_page2(
                            browser.page_source)
                        idx1_extended = {}
                        for sub2 in idx1:
                            idx1_extended[sub2] = {}
                            for sub3 in idx1[sub2]:
                                if sub3 in footnote_idx:
                                    idx1_extended[sub2][sub3] = footnote_idx[sub3]
                        idx[sub0][sub1][frequency_name] = idx1_extended

                        save_table(
                            sub0, sub1, frequency_name, i_group, results_idx)
                        go_back_to_page1(browser)

                    go_back_to_page0(browser)

    save_contents(idx, 'extended')

    browser.quit()


if __name__ == '__main__':
    init()
    run()
