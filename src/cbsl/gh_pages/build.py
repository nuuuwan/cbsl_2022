import math
import os

from utils.xmlx import _

from cbsl._constants import DIR_GH_PAGES, URL
from cbsl._utils import log
from cbsl.core.data import get_idx1234, read_file

MAX_COLS_PER_TABLE = 10


def sub_to_title(sub):
    return sub.replace('-', ' ').title()


def format_cell(s, i_col):
    if i_col == 0:
        return sub_to_title(s)
    return s


def init():
    os.system(f'rm -rf {DIR_GH_PAGES}')
    os.system(f'mkdir -p {DIR_GH_PAGES}')


def copy_files():
    for file_only in ['styles.css']:
        os.system(f'cp src/cbsl/gh_pages/{file_only} {DIR_GH_PAGES}/')


def get_sub3_html_file_only(sub3):
    return f'{sub3}.html'


def render_tables(data_list):
    n_cols = len(data_list[0].keys()) - 1
    n_groups = math.ceil(n_cols / MAX_COLS_PER_TABLE)

    key_list = list(data_list[0].keys())
    rendered_tables = []
    for i_group in range(0, n_groups):
        col_min = i_group * MAX_COLS_PER_TABLE
        col_max = min(col_min + MAX_COLS_PER_TABLE, n_cols)
        i_cols = [0] + [i + 1 for i in range(col_min, col_max)]

        thead = _('thead', [
            _('tr', list(map(
                lambda i_col: _('th', key_list[i_col]),
                i_cols,
            ))),
        ])
        tbody = _('tbody', list(map(
            lambda d: _('tr', list(map(
                lambda i_col: _(
                    'td',
                    format_cell(d[key_list[i_col]], i_col),
                    {'class': f'td-{i_col}'}
                ),
                i_cols,
            ))),
            data_list,
        )))
        rendered_table = _('table', [thead, tbody])
        rendered_tables.append(rendered_table)
    return rendered_tables


def render_file(sub1, sub2, sub3, file_only, sub4_list):
    data_list = read_file(sub1, sub2, sub3, file_only)
    rendered_tables = render_tables(data_list)
    return _('div', [
        _('h2', file_only),
    ] + rendered_tables, {'class': 'div-file'})


def build_sub3(sub1, sub2, sub3, file_to_sub4s):
    head = _('head', [
        _('link', None, {'rel': 'stylesheet', 'href': 'styles.css'})
    ])

    rendered_files = list(map(
        lambda x: render_file(sub1, sub2, sub3, x[0], x[1]),
        file_to_sub4s.items(),
    ))

    body = _('body', [
        _('h2', 'Central Bank of Sri Lanka - Data Library'),
        _('h1', sub_to_title(sub3)),
        _('h3', [
            _('span', 'Source:'),
            _('a', URL, {'href': URL})
        ]),
    ] + rendered_files)
    html = _('html', [head, body])

    html_file_only = get_sub3_html_file_only(sub3)
    html_file = os.path.join(DIR_GH_PAGES, html_file_only)
    html.store(html_file)
    log.info(f'Stored {html_file}')

    return html_file_only


def render_sub3(sub1, sub2, sub3, file_to_sub4s):
    html_file_only = build_sub3(sub1, sub2, sub3, file_to_sub4s)
    return _('div', [
        _('div', [
            _('a', [
                _('span', sub_to_title(sub3)),
            ], {'href': html_file_only}),
        ], {'class': 'div-sub3-title'}),
    ], {'class': 'div-sub3'})


def render_sub2(sub1, sub2, idx34):
    rendered_sub3s = list(map(
        lambda x: render_sub3(sub1, sub2, x[0], x[1]),
        idx34.items(),
    ))

    return _('div', [
        _('h2', sub_to_title(sub2)),
    ] + rendered_sub3s, {'class': 'div-sub2'})


def render_sub1(sub1, idx234):
    rendered_sub2s = list(map(
        lambda x: render_sub2(sub1, x[0], x[1]),
        list(idx234.items()),
    ))

    return _('div', [
        _('h1', sub_to_title(sub1)),
    ] + rendered_sub2s, {'class': 'div-sub1'})


def main():
    # git_checkout()
    init()
    copy_files()

    idx1234 = get_idx1234()

    rendered_sub1s = list(map(
        lambda x: render_sub1(x[0], x[1]),
        list(idx1234.items()),
    ))

    head = _('head', [
        _('link', None, {'rel': 'stylesheet', 'href': 'styles.css'})
    ])
    body = _('body', [
        _('h2', 'Central Bank of Sri Lanka'),
        _('h1', 'Data Library'),
        _('h3', [
            _('span', 'Source:'),
            _('a', URL, {'href': URL})
        ]),
    ] + rendered_sub1s)
    html = _('html', [head, body])

    html_file = os.path.join(DIR_GH_PAGES, 'index.html')
    html.store(html_file)
    log.info(f'Stored {html_file}')


if __name__ == '__main__':
    main()
