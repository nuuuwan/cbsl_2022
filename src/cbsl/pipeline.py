import os

from utils import jsonx

from cbsl._constants import DIR_DATA
from cbsl._utils import log
from cbsl.frequency import FREQUNCY_CONFIG
from cbsl.parsers import parse_page0, parse_page1, parse_page2
from cbsl.scrapers import (init, open_browser, open_page0, open_page1,
                           open_page2)


def run():
    browser = open_browser()
    open_page0(browser)
    idx = parse_page0(browser.page_source)

    for sub0 in idx:
        for i_sub1, sub1 in enumerate(list(idx[sub0])):
            for frequency_name in FREQUNCY_CONFIG:
                if open_page1(browser, sub0, i_sub1, sub1, frequency_name):
                    idx1 = parse_page1(browser.page_source)

                    open_page2(browser)
                    footnote_idx = parse_page2(browser.page_source)
                    idx1_extended = {}
                    for sub2 in idx1:
                        idx1_extended[sub2] = {}
                        for sub3 in idx1[sub2]:
                            idx1_extended[sub2][sub3] = footnote_idx[sub3]
                    idx[sub0][sub1][frequency_name] = idx1_extended
                    break
            break
        break

    data_file = os.path.join(DIR_DATA, 'contents.json')
    jsonx.write(data_file, idx)
    n_sub0 = len(idx)
    log.info(f'Wrote {n_sub0} sub0s to {data_file}')

    browser.quit()


if __name__ == '__main__':
    init()
    run()
