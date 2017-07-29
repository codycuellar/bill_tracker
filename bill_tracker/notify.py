#! /usr/bin/env python
import core
import logging
import config as cfg


def main():
    core.load_json()
    core.check_due_dates()
    core.all_bills_to_json()
    core.send_email(DEBUG=True)

if __name__ == '__main__':
    logger = logging.getLogger()
    cfg.configure_logging(logger, logname='notify',
                          log_level=logging.DEBUG,
                          file_level=logging.DEBUG,
                          console_level=logging.DEBUG)
    main()