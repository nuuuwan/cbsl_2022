"""Utils."""
import argparse

from utils import logx

log = logx.get_logger('cbsl')


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-mode', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    if args.test_mode:
        log.warning('Running in TEST MODE')
    else:
        log.debug('NOT running in TEST MODE')
    return args
