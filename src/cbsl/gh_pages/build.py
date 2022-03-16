import math
import os

from utils.xmlx import _

from cbsl._constants import DIR_GH_PAGES, URL
from cbsl._utils import is_test_mode, log
from cbsl.core.data import get_idx1234, git_checkout, read_file, read_metadata

MAX_COLS_PER_TABLE = 10


def sub_to_title(sub):
    return sub.replace('-', ' ').title()


def format_cell(k, d):
    v = d.get(k, '')
    if k == 'sub4':
        return sub_to_title(v)
    return v


def format_header_cell(k):
    if k == 'sub4':
        return 'Subject'
    return k


def init():
    os.system(f'rm -rf {DIR_GH_PAGES}')
    os.system(f'mkdir -p {DIR_GH_PAGES}')


def copy_files():
    for file_only in ['styles.css']:
        os.system(f'cp src/cbsl/gh_pages/{file_only} {DIR_GH_PAGES}/')


def get_sub3_html_file_only(sub3):
    return f'{sub3}.html'


def get_all_keys(data_list):
    k_set = set()
    for d in data_list:
        for k in d:
            k_set.add(k)
    k_set.remove('sub4')
    return ['sub4'] + list(k_set)


def render_metadata(
    metadata_idx,
):
    data_list = list(metadata_idx.values())
    key_list = get_all_keys(data_list)
    thead = _('thead', [
        render_header_row(key_list),
    ])
    tbody = _('tbody', list(map(
        lambda d: render_row(key_list, d),
        data_list,
    )))
    return _('table', [thead, tbody])


def render_header_row(key_list):
    return _('tr', list(map(
        lambda k: _('th', format_header_cell(k)),
        key_list,
    )))


def render_row(key_list, d):
    return _('tr', list(map(
        lambda k: _('td', format_cell(k, d)),
        key_list,
    )))


def render_table(
    data_list,
    key_list,
):
    thead = _('thead', [
        render_header_row(key_list),
    ])
    tbody = _('tbody', list(map(
        lambda d: render_row(key_list, d),
        data_list,
    )))
    return _('table', [thead, tbody])


def get_non_empty_result_key_list(data_list):
    key_list = get_all_keys(data_list)
    non_empty_key_list = []
    for k in key_list:
        if k == 'sub4':
            continue
        non_empty = False
        for d in data_list:
            if d[k]:
                non_empty = True
                break
        if non_empty:
            non_empty_key_list.append(k)
    return list(reversed(sorted(non_empty_key_list)))


def render_tables(data_list):
    all_result_key_list = get_non_empty_result_key_list(data_list)
    n_cols = len(all_result_key_list)
    n_groups = math.ceil(n_cols / MAX_COLS_PER_TABLE)

    rendered_tables = []
    for i_group in range(0, n_groups):
        col_min = i_group * MAX_COLS_PER_TABLE
        col_max = min(col_min + MAX_COLS_PER_TABLE, n_cols)
        key_list = ['sub4'] + [all_result_key_list[i]
                               for i in range(col_min, col_max)]
        rendered_tables.append(
            render_table(
                data_list,
                key_list,
            )
        )
    return rendered_tables


def render_file(sub1, sub2, sub3, file_only, sub4_list):
    data_list = read_file(sub1, sub2, sub3, file_only)
    metadata_idx = read_metadata(sub1, sub2, sub3, file_only)

    rendered_metadata = render_metadata(metadata_idx)
    rendered_tables = render_tables(data_list)
    return _('div', [
        _('h2', file_only),
        rendered_metadata,
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


def render_sub1(sub1, idx234, test_mode):
    idx234_items = list(idx234.items())
    if test_mode:
        idx234_items = idx234_items[:1]

    rendered_sub2s = list(map(
        lambda x: render_sub2(sub1, x[0], x[1]),
        idx234_items,
    ))

    return _('div', [
        _('h1', sub_to_title(sub1)),
    ] + rendered_sub2s, {'class': 'div-sub1'})


def main(test_mode):
    if not test_mode:
        git_checkout()
    init()
    copy_files()

    idx1234 = get_idx1234()

    idx1234_items = list(idx1234.items())
    if test_mode:
        idx1234_items = idx1234_items[:1]

    rendered_sub1s = list(map(
        lambda x: render_sub1(x[0], x[1], test_mode),
        idx1234_items,
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
    main(is_test_mode())
