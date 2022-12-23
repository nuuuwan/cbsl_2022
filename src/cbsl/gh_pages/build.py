import math
import os

from utils import colorx, timex
from utils.xmlx import _

from cbsl._constants import DIR_GH_PAGES, URL
from cbsl._utils import is_test_mode, log
from cbsl.core.data import get_idx1234, git_checkout, read_file, read_metadata

MAX_COLS_PER_TABLE = 10
METADATA_FIELDS = [
    'Sector',
    'scale',
    'GeoArea',
    'Source',
    'Data last updated',
    'unit',
    'Update frequency',
    'Note',
]

HEAD = _(
        'head',
        [
            _('meta', None, {'charset': 'UTF-8'}),
            _('link', None, {'rel': 'stylesheet', 'href': 'styles.css'}),
            _('link', None, {'rel': 'stylesheet', 'href': 'https://fonts.googleapis.com/css?family=PT Sans'}),
        ],
    )
    


def parse_float(s):
    s = s.replace(',', '')
    try:
        f = (float)(s)
        return f
    except ValueError:
        return 0


def sub_to_title(sub):
    return sub.replace('-', ' ').title()


def humanize_number(x):
    ax = abs(x)
    if ax > 1_000_000_000_000:
        x_x = x / 1_000_000_000_000
        return f'{x_x:.1f}', 'T'

    if ax > 1_000_000_000:
        x_x = x / 1_000_000_000
        return f'{x_x:.1f}', 'B'

    if ax > 1_000_000:
        x_x = x / 1_000_000
        return f'{x_x:.1f}', 'M'

    if ax > 1_000:
        x_x = x / 1_000
        return f'{x_x:.1f}', 'K'

    return f'{x}', ''


def format_cell(k, d, metadata, value_to_rank_p):
    v = d.get(k, '')
    display_unit = ''
    background = 'white'
    class_name = ''
    if k == 'sub4':
        text = sub_to_title(v)
        class_name = 'div-cell-text'
    elif k == 'Data last updated':
        try:
            ut = timex.parse_time(v, '%Y-%m-%d')
            text = timex.format_time(ut, '%b %d, %Y')
        except BaseException:
            text = ''
        class_name = 'div-cell-date'
    elif k in METADATA_FIELDS:
        text = v
        class_name = 'div-cell-text-metadata'
    else:
        unit = metadata.get('unit')
        scale = metadata.get('scale')
        value = parse_float(v)
        if value == 0:
            text = '-'
        else:
            rank_p = value_to_rank_p[value]
            hue = 0 + 240 * (1 - rank_p)
            lightness = 0.8
            background = colorx.random_hsl(hue=hue, lightness=lightness)
            if unit in ['Thousands', '000 persons']:
                value *= 1000
            if scale in ['Million', 'Mn.']:
                value *= 1000_000

            text, display_unit = humanize_number(value)
            class_name = 'div-cell-number'

            if (unit and unit[0] == '%') or unit in ['%', 'Percentage']:
                text, display_unit = f'{value:.1f}', '%'
            elif unit in ['Per 1,000 Persons', 'Per 1000 Persons']:
                text, display_unit = f'{value:.1f}', 'per 1000'

            if unit in ['Rs.', 'Kg', 'm3', 'Sq. km.']:
                display_unit += ' ' + unit

    return [
        _(
            'div',
            [
                _(
                    'div',
                    [
                        _('div', text, {'class': class_name}),
                        _('div', display_unit, {'class': 'div-cell-unit'}),
                    ],
                    {'class': 'div-cell-inner'},
                )
            ],
            {'style': f'background:{background}'},
        )
    ]


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
    return ['sub4'] + list(sorted(k_set))


def render_metadata(
    metadata_idx,
):
    data_list = list(metadata_idx.values())
    key_list = get_all_keys(data_list)
    thead = _(
        'thead',
        [
            render_header_row(key_list),
        ],
    )
    tbody = _(
        'tbody',
        list(
            map(
                lambda d: render_row(key_list, d, {}),
                data_list,
            )
        ),
    )
    return _('table', [thead, tbody])


def render_header_row(key_list):
    return _(
        'tr',
        list(
            map(
                lambda k: _('th', format_header_cell(k)),
                key_list,
            )
        ),
    )


def render_row(key_list, d, metadata_idx):
    sorted_values = sorted(
        list(
            filter(
                lambda x: x,
                list(
                    map(
                        lambda v: parse_float(v),
                        list(d.values())[1:],
                    )
                ),
            )
        )
    )
    n = len(sorted_values)
    value_to_rank_p = dict(
        list(
            map(
                lambda x: [x[1], x[0] / n],
                enumerate(sorted_values),
            )
        )
    )

    metadata = metadata_idx.get(d['sub4'])
    return _(
        'tr',
        list(
            map(
                lambda k: _(
                    'td',
                    format_cell(k, d, metadata, value_to_rank_p),
                ),
                key_list,
            )
        ),
    )


def render_table(
    data_list,
    key_list,
    metadata_idx,
):
    data_list = sorted(data_list, key=lambda d: d['sub4'])
    thead = _(
        'thead',
        [
            render_header_row(key_list),
        ],
    )
    tbody = _(
        'tbody',
        list(
            map(
                lambda d: render_row(key_list, d, metadata_idx),
                data_list,
            )
        ),
    )
    table_title = key_list[1] + ' to ' + key_list[-1]
    return _(
        'div',
        [
            _('h3', table_title),
            _('table', [thead, tbody]),
        ],
        {'class': 'div-single-table'},
    )


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


def render_tables(data_list, metadata_idx):
    all_result_key_list = get_non_empty_result_key_list(data_list)
    n_cols = len(all_result_key_list)
    n_groups = math.ceil(n_cols / MAX_COLS_PER_TABLE)

    rendered_tables = []
    for i_group in range(0, n_groups):
        col_min = i_group * MAX_COLS_PER_TABLE
        col_max = min(col_min + MAX_COLS_PER_TABLE, n_cols)
        key_list = ['sub4'] + [
            all_result_key_list[i] for i in range(col_min, col_max)
        ]
        rendered_tables.append(
            render_table(
                data_list,
                key_list,
                metadata_idx,
            )
        )
    return rendered_tables


def render_file(sub1, sub2, sub3, file_only, sub4_list):
    data_list = read_file(sub1, sub2, sub3, file_only)
    metadata_idx = read_metadata(sub1, sub2, sub3, file_only)

    rendered_metadata = render_metadata(metadata_idx)
    rendered_tables = render_tables(data_list, metadata_idx)
    return _(
        'div',
        [
            _('h2', file_only),
            rendered_metadata,
        ]
        + rendered_tables,
        {'class': 'div-file'},
    )


def build_sub3(sub1, sub2, sub3, file_to_sub4s):
    rendered_files = list(
        map(
            lambda x: render_file(sub1, sub2, sub3, x[0], x[1]),
            file_to_sub4s.items(),
        )
    )

    body = _(
        'body',
        [
            _('h2', 'Central Bank of Sri Lanka - Data Library'),
            _('h1', sub_to_title(sub3)),
            _('h3', [_('span', 'Source:'), _('a', URL, {'href': URL})]),
        ]
        + rendered_files,
    )
    html = _('html', [HEAD, body])

    html_file_only = get_sub3_html_file_only(sub3)
    html_file = os.path.join(DIR_GH_PAGES, html_file_only)
    html.store(html_file)
    log.info(f'Stored {html_file}')

    return html_file_only


def render_sub3(sub1, sub2, sub3, file_to_sub4s):
    html_file_only = build_sub3(sub1, sub2, sub3, file_to_sub4s)
    return _(
        'div',
        [
            _(
                'div',
                [
                    _(
                        'a',
                        [
                            _('span', sub_to_title(sub3)),
                        ],
                        {'href': html_file_only},
                    ),
                ],
                {'class': 'div-sub3-title'},
            ),
        ],
        {'class': 'div-sub3'},
    )


def render_sub2(sub1, sub2, idx34):
    rendered_sub3s = list(
        map(
            lambda x: render_sub3(sub1, sub2, x[0], x[1]),
            idx34.items(),
        )
    )

    return _(
        'div',
        [
            _('h2', sub_to_title(sub2)),
        ]
        + rendered_sub3s,
        {'class': 'div-sub2'},
    )


def render_sub1(sub1, idx234, test_mode):
    idx234_items = list(idx234.items())
    if test_mode:
        idx234_items = idx234_items[:1]

    rendered_sub2s = list(
        map(
            lambda x: render_sub2(sub1, x[0], x[1]),
            idx234_items,
        )
    )

    return _(
        'div',
        [
            _('h1', sub_to_title(sub1)),
        ]
        + rendered_sub2s,
        {'class': 'div-sub1'},
    )


def main(test_mode):
    if not test_mode:
        git_checkout()
    init()
    copy_files()

    idx1234 = get_idx1234()

    idx1234_items = list(idx1234.items())
    if test_mode:
        idx1234_items = idx1234_items[:1]

    rendered_sub1s = list(
        map(
            lambda x: render_sub1(x[0], x[1], test_mode),
            idx1234_items,
        )
    )

    body = _(
        'body',
        [
            _('h2', 'Central Bank of Sri Lanka'),
            _('h1', 'Data Library'),
            _('h3', [_('span', 'Source:'), _('a', URL, {'href': URL})]),
        ]
        + rendered_sub1s,
    )
    html = _('html', [HEAD, body])

    html_file = os.path.join(DIR_GH_PAGES, 'index.html')
    html.store(html_file)
    log.info(f'Stored {html_file}')


if __name__ == '__main__':
    main(is_test_mode())
