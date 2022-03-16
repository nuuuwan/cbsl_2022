import os

from utils.xmlx import _

from cbsl._constants import DIR_GH_PAGES, URL
from cbsl._utils import log
from cbsl.core.data import get_idx1234, git_checkout


def sub_to_title(sub):
    return sub.replace('-', ' ').title()


def init():
    os.system(f'rm -rf {DIR_GH_PAGES}')
    os.system(f'mkdir -p {DIR_GH_PAGES}')


def copy_files():
    for file_only in ['styles.css']:
        os.system(f'cp src/cbsl/gh_pages/{file_only} {DIR_GH_PAGES}/')


def render_sub3(sub3, idx4):
    return _('div', [
        _('div', sub_to_title(sub3), {'class': 'div-sub3-title'}),
    ], {'class': 'div-sub3'})


def render_sub2(sub2, idx34):
    rendered_sub3s = list(map(
        lambda x: render_sub3(x[0], x[1]),
        idx34.items(),
    ))

    return _('div', [
        _('div', sub_to_title(sub2), {'class': 'div-sub2-title'}),
    ] + rendered_sub3s, {'class': 'div-sub2'})


def render_sub1(sub1, idx234):
    rendered_sub2s = list(map(
        lambda x: render_sub2(x[0], x[1]),
        idx234.items(),
    ))

    return _('div', [
        _('div', sub_to_title(sub1), {'class': 'div-sub1-title'}),
    ] + rendered_sub2s, {'class': 'div-sub1'})


def main():
    git_checkout()
    init()
    copy_files()

    idx1234 = get_idx1234()

    rendered_sub1s = list(map(
        lambda x: render_sub1(x[0], x[1]),
        idx1234.items(),
    ))

    head = _('head', [
        _('link', None, {'rel': 'stylesheet', 'href': 'styles.css'})
    ])
    body = _('body', [
        _('div', 'Central Bank of Sri Lanka', {'class': 'div-supertitle'}),
        _('div', 'Data Library', {'class': 'div-title'}),
        _('div', [
            _('span', 'Source:'),
            _('a', URL, {'href': URL})
        ], {'class': 'div-source'}),
    ] + rendered_sub1s)
    html = _('html', [head, body])

    html_file = os.path.join(DIR_GH_PAGES, 'index.html')
    html.store(html_file)
    log.info(f'Stored {html_file}')


if __name__ == '__main__':
    main()
