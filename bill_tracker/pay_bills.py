#! /usr/bin/env python
import core
import config as cfg
import logging



if __name__ == '__main__':
    logger = logging.getLogger()

    cfg.configure_logging(logger, logname='pay_bills',
                          log_level=logging.info,
                          file_level=logging.INFO,
                          console_level=logging.DEBUG)

    core.load_json()

    for bill in [b for b in core.current_bills if not b.automatic]:
        if bill.due:
            print '\nDid you pay', bill.name, '? (y/n)'
            response = raw_input("> ")
            logger.debug('User input: %s' % response)
            if response.lower() in ['yes', 'y']:
                bill.pay_bill()
                print "Bill %s marked as paid." % bill.name
            else:
                print 'Bill not paid.'
                continue

    core.all_bills_to_json()
