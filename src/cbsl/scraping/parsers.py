import re

from bs4 import BeautifulSoup

from cbsl._utils import log
from cbsl.scraping.scrapers import (CLASS_TABLE0, ID_TABLE_PAGE1_SEARCH_LIST,
                                    ID_TABLE_PAGE2_FOOTNOTES,
                                    ID_TABLE_PAGE2_RESULTS)

MIN_SUB3_LEN = 6


def clean(s):
    s = s.replace(' -', '-')
    s = s.replace('- ', '-')
    s = s.replace('--', '-')
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def make_sub(s, parent_s=''):
    s = clean(s)
    s = s.lower()
    s = s.replace(' ', '-')
    s = re.sub(r'-+', '-', s).strip()
    s = s.replace(parent_s, '').strip('-')

    if s == '':
        return parent_s

    return s


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


def parse_step3_footnotes(soup, sub3):
    table = soup.find('table', {'id': ID_TABLE_PAGE2_FOOTNOTES})
    footnote_idx = {}
    cur_footnote = None
    cur_sub4 = None
    for tr in table.find_all('tr'):
        td = tr.find_all('td')[1]
        span = td.find('span')
        text = clean(span.text)
        if 'bold' in span['style']:
            new_sub4 = make_sub(text.partition(')')[2], sub3)
            if len(new_sub4) > MIN_SUB3_LEN:
                if cur_footnote:
                    footnote_idx[cur_sub4] = cur_footnote
                cur_footnote = {'sub4': new_sub4}
                cur_sub4 = new_sub4
        else:
            k, ___, v = text.partition(':')
            cur_footnote[k] = v

    if cur_footnote:
        footnote_idx[cur_sub4] = cur_footnote
    return footnote_idx


def parse_step3_results(soup, sub3):
    table = soup.find('table', {'id': ID_TABLE_PAGE2_RESULTS})
    headers = None
    results_idx = {}
    for row in table.find_all('tr'):
        if not headers:
            th_list = list(
                map(
                    lambda th: clean(th.text),
                    row.find_all('th'),
                )
            )
            headers = th_list[4:]
        else:
            td_list = list(
                map(
                    lambda th: clean(th.text),
                    row.find_all('td'),
                )
            )

            if td_list[0] != '':
                sub4, unit, scale = td_list[1:4]
                sub4 = make_sub(sub4, sub3)

                results = dict(
                    zip(
                        headers,
                        td_list[4:],
                    )
                )
                results_idx[sub4] = {
                    'sub4': sub4,
                    'unit': unit,
                    'scale': scale,
                    'results': results,
                }

    return results_idx


def parse_step3(html, sub3):
    log.debug('Parsing step3...')
    soup = BeautifulSoup(html, 'html.parser')
    footnote_idx = parse_step3_footnotes(soup, sub3)
    results_idx = parse_step3_results(soup, sub3)
    return [footnote_idx, results_idx]
