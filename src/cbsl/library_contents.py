import os
import shutil

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from utils import jsonx

from cbsl._utils import log

URL = 'https://www.cbsl.lk/eresearch/'
DIR_ROOT = '/tmp/cbsl'
DIR_DATA = os.path.join(DIR_ROOT, 'data')


def init():
    shutil.rmtree(DIR_ROOT, ignore_errors=True)
    os.mkdir(DIR_ROOT)
    os.mkdir(DIR_DATA)


def scrape():
    log.debug(f'[slow] Openning {URL} in browser...')
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)
    browser.get(URL)
    html = browser.page_source

    soup = BeautifulSoup(html, 'html.parser')
    library_contents = {}
    for table in soup.find_all('table', {'class': 'subjectgrid'}):
        tr_list = [tr for tr in table.find_all('tr')]
        subject = tr_list[0].text.strip()
        sub_subjects = list(map(
            lambda tr: tr.find_all('td')[1].text.strip(),
            tr_list[1:],
        ))
        library_contents[subject] = sub_subjects

    data_file = os.path.join(DIR_DATA, 'library_contents.json')
    jsonx.write(data_file, library_contents)
    n_subject = len(library_contents)
    log.info(f'Wrote {n_subject} subjects to {data_file}')

    browser.quit()


if __name__ == '__main__':
    init()
    scrape()
