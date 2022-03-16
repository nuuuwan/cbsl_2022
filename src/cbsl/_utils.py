"""Utils."""
import argparse

from utils import logx

log = logx.get_logger('cbsl')


def is_test_mode():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--prod-mode',
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        '--test-mode',
        action=argparse.BooleanOptionalAction,
    )
    args = parser.parse_args()
    test_mode = bool(args.test_mode or not args.prod_mode)
    if test_mode:
        log.warning('Running in TEST MODE')
    else:
        log.debug('NOT running in TEST MODE')
    return test_mode
