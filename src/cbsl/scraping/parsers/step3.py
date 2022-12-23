from bs4 import BeautifulSoup

from cbsl._utils import log
from cbsl.scraping.parsers.common import clean, make_sub
from cbsl.scraping.navigators import (ID_TABLE_PAGE2_FOOTNOTES,
                                    ID_TABLE_PAGE2_RESULTS)

MIN_SUB3_LEN = 6


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
