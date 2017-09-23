#! /usr/bin/env python
import core
import logging
import config as cfg
import argparse


def main(DEBUG=False):
    core.load_bills()
    core.check_due_dates()
    core.all_bills_to_json()
    core.send_email(DEBUG=DEBUG)


if __name__ == '__main__':
    logger = logging.getLogger()

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help='Enable debug mode.')
    args = parser.parse_args()

    if args.debug:
        cfg.configure_logging(logger, logname='notify',
                              log_level=logging.DEBUG,
                              file_level=logging.DEBUG,
                              console_level=logging.DEBUG)
    else:
        cfg.configure_logging(logger, logname='notify',
                              log_level=logging.INFO,
                              file_level=logging.INFO,
                              console_level=logging.DEBUG)
    main(DEBUG=args.debug)
