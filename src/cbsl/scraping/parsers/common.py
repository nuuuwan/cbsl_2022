import re

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
