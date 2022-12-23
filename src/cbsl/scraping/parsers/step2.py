from bs4 import BeautifulSoup

from cbsl._utils import log
from cbsl.scraping.navigators import ID_TABLE_PAGE1_SEARCH_LIST
from cbsl.scraping.parsers.common import make_sub

MIN_SUB3_LEN = 6


def parse_step2(html, sub2):
    log.debug('Parsing step2...')
    soup = BeautifulSoup(html, 'html.parser')
    idx = {}
    n_sub3, n_sub4 = 0, 0
    for table in soup.find_all('table', {'id': ID_TABLE_PAGE1_SEARCH_LIST}):
        for tr in table.find_all('tr'):
            td_list = tr.find_all('td')
            if len(td_list) < 3:
                continue
            td = td_list[2]
            if 'GdHDColor1' in td.attrs['class']:
                sub3 = make_sub(td.text, sub2)
                idx[sub3] = {}
                n_sub3 += 1

            else:
                sub4 = make_sub(td.text, sub3)
                if sub4:
                    idx[sub3][sub4] = {}
                    log.info(f'Found ../{sub2}/{sub3}/{sub4}')
                    n_sub4 += 1
    log.info(f'Found {n_sub3} sub3s, {n_sub4} sub4s')
    return idx
