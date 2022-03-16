import os
import shutil

from utils import jsonx, tsv

from cbsl._constants import DIR_DATA, DIR_ROOT
from cbsl._utils import log

GROUP_SIZE = 30


def init():
    shutil.rmtree(DIR_ROOT, ignore_errors=True)
    os.mkdir(DIR_ROOT)
    os.mkdir(DIR_DATA)


def save_results(
        sub1,
        sub2,
        frequency_name,
        i_group,
        results_idx,
        footnote_idx):
    dir = os.path.join(
        DIR_DATA,
        sub1,
        sub2,
    ).replace(' ', '-').lower()

    if not os.path.exists(dir):
        os.system(f'mkdir -p "{dir}"')

    data_list = []
    metadata_idx = {}
    for sub4, d in results_idx.items():
        data_list.append(
            {
                'sub4': sub4,
            } | dict(reversed(d['results'].items()))
        )
        metadata_idx[sub4] = {
            'sub4': sub4,
            'unit': d['unit'],
            'scale': d['scale'],
        } | footnote_idx.get(sub4, {})

    frequency_name_str = frequency_name.replace(' ', '-').lower()
    file_prefix = f'{frequency_name_str}-{i_group:03d}'

    tsv_file = os.path.join(dir, f'{file_prefix}.tsv')
    tsv.write(tsv_file, data_list)
    n_rows = len(data_list)
    n_cols = len(data_list[0])
    log.info(f'Wrote {tsv_file} ({n_rows}x{n_cols})')

    metadata_file = os.path.join(dir, f'{file_prefix}.metadata.json')
    jsonx.write(metadata_file, metadata_idx)
    log.info(f'Wrote {metadata_file}')


def save_contents(idx, prefix):
    data_file = os.path.join(DIR_DATA, f'contents.{prefix}.json')
    jsonx.write(data_file, idx)
    n_sub1 = len(idx)
    log.info(f'Wrote {n_sub1} sub1s to {data_file}')
