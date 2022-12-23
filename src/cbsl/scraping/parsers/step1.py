from bs4 import BeautifulSoup

from cbsl._utils import log
from cbsl.scraping.parsers.common import make_sub
from cbsl.scraping.scrapers import CLASS_TABLE0


def parse_step1(html):
    log.debug('Parsing step1...')
    soup = BeautifulSoup(html, 'html.parser')
    idx = {}
    n_sub1, n_sub2 = 0, 0
    for table in soup.find_all('table', {'class': CLASS_TABLE0}):
        tr_list = [tr for tr in table.find_all('tr')]
        sub1 = make_sub(tr_list[0].text)
        n_sub1 += 1
        idx[sub1] = {}
        for tr in tr_list[1:]:
            sub2 = make_sub(tr.find_all('td')[1].text)
            idx[sub1][sub2] = {}
            log.info(f'Found {sub1}/{sub2}')
            n_sub2 += 1
    log.info(f'Found {n_sub1} sub1s, {n_sub2} sub2s')
    return idx
