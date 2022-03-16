import os

from utils import jsonx, tsv

from cbsl._constants import DIR_DATA
from cbsl._utils import log

IDX2_FILE = os.path.join(DIR_DATA, 'contents.basic.json')


def git_checkout():
    os.system(f'rm -rf {DIR_DATA}')
    os.system(f'mkdir -p {DIR_DATA}')

    os.system(';'.join([
        f'cd {DIR_DATA}',
        'git clone https://github.com/nuuuwan/cbsl.git .',
        'git checkout data',
    ]))
    log.info(f'git clone https://github.com/nuuuwan/cbsl.git -> {DIR_DATA}')


def get_idx12():
    return jsonx.read(IDX2_FILE)


def get_idx1234():
    idx12 = get_idx12()
    tree = {}
    for sub1 in idx12:
        tree[sub1] = {}
        for sub2 in idx12[sub1]:
            tree[sub1][sub2] = {}
            dir12 = os.path.join(DIR_DATA, sub1, sub2)
            if not os.path.exists(dir12):
                continue

            for sub3 in os.listdir(dir12):
                dir123 = os.path.join(dir12, sub3)
                if not os.path.isdir(dir123):
                    continue
                tree[sub1][sub2][sub3] = {}

                for file_only in os.listdir(dir123):
                    if file_only[-4:] != '.tsv':
                        continue
                    tree[sub1][sub2][sub3][file_only] = []
                    data_file = os.path.join(dir123, file_only)
                    data_list = tsv.read(data_file)
                    for d in data_list:
                        sub4 = d['sub4']
                        tree[sub1][sub2][sub3][file_only].append(sub4)
    return tree


def read_file(sub1, sub2, sub3, file_only):
    dir123 = os.path.join(DIR_DATA, sub1, sub2, sub3)
    tsv_file = os.path.join(dir123, file_only)
    return tsv.read(tsv_file)


def read_metadata(sub1, sub2, sub3, file_only):
    dir123 = os.path.join(DIR_DATA, sub1, sub2, sub3)
    tsv_file = os.path.join(dir123, file_only)
    metadata_file = tsv_file.replace('.tsv', '.metadata.json')
    return jsonx.read(metadata_file)


if __name__ == '__main__':
    print(get_idx1234())
