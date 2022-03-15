import re

from bs4 import BeautifulSoup

from cbsl._utils import log

CLASS_TABLE0 = 'subjectgrid'
ID_TABLE_PAGE1_SEARCH_LIST = 'ContentPlaceHolder1_grdSearchList'
ID_TABLE_PAGE2_FOOTNOTES = 'ContentPlaceHolder1_grdFootNotes'
ID_TABLE_PAGE2_RESULTS = 'ContentPlaceHolder1_grdResult'
MIN_SUB3_LEN = 6


def clean(s):
    s = s.replace(' -', '-')
    s = s.replace('- ', '-')
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def parse_page0(html):
    log.debug('Parsing page0...')
    soup = BeautifulSoup(html, 'html.parser')
    idx = {}
    n_sub0, n_sub1 = 0, 0
    for table in soup.find_all('table', {'class': CLASS_TABLE0}):
        tr_list = [tr for tr in table.find_all('tr')]
        sub0 = clean(tr_list[0].text)
        n_sub0 += 1
        idx[sub0] = {}
        for tr in tr_list[1:]:
            sub1 = clean(tr.find_all('td')[1].text)
            idx[sub0][sub1] = {}
            n_sub1 += 1
    log.info(f'Found {n_sub0} sub0s, {n_sub1} sub1s')
    return idx


def parse_page1(html):
    log.debug('Parsing page1...')
    soup = BeautifulSoup(html, 'html.parser')
    idx = {}
    n_sub2, n_sub3 = 0, 0
    for table in soup.find_all('table', {'id': ID_TABLE_PAGE1_SEARCH_LIST}):
        for tr in table.find_all('tr'):
            td_list = tr.find_all('td')
            if len(td_list) < 3:
                continue
            td = td_list[2]
            if 'GdHDColor1' in td.attrs['class']:
                sub2 = clean(td.text)
                idx[sub2] = {}
                n_sub2 += 1

            else:
                sub3 = clean(td.text)
                if sub3:
                    idx[sub2][sub3] = {}
                    n_sub3 += 1
    log.info(f'Found {n_sub2} sub2s, {n_sub3} sub3s')
    return idx


def parse_page2_footnotes(soup):
    table = soup.find('table', {'id': ID_TABLE_PAGE2_FOOTNOTES})
    footnote_idx = {}
    cur_footnote = None
    cur_sub3 = None
    for tr in table.find_all('tr'):
        td = tr.find_all('td')[1]
        span = td.find('span')
        text = clean(span.text)
        if 'bold' in span['style']:
            new_sub3 = clean(text.partition(')')[2])
            if len(new_sub3) > MIN_SUB3_LEN:
                if cur_footnote:
                    footnote_idx[cur_sub3] = cur_footnote
                cur_footnote = {'sub3': new_sub3}
                cur_sub3 = new_sub3
        else:
            k, ___, v = text.partition(':')
            cur_footnote[k] = v

    if cur_footnote:
        footnote_idx[cur_sub3] = cur_footnote
    return footnote_idx


def parse_page2_results(soup):
    return {}


def parse_page2(html):
    log.debug('Parsing page2...')
    soup = BeautifulSoup(html, 'html.parser')
    footnote_idx = parse_page2_footnotes(soup)
    results_idx = parse_page2_results(soup)
    return [footnote_idx, results_idx]
