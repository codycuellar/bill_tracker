#! /usr/bin/env python
import core
import config as cfg
import logging

logger = logging.getLogger()


def startup():
	cfg.configure_logging(logger, logname='pay_bills',
						  log_level=logging.INFO,
						  file_level=logging.INFO,
						  console_level=logging.DEBUG)
	main()


def main():
	core.load_bills()

	for bill in [b for b in core.current_bills if not b.automatic]:
		if bill.due:
			print '\nDid you pay', bill.name, '? (y/n)'
			response = raw_input("> ")
			logger.debug('User input: %s' % response)
			if response.lower() in ['yes', 'y']:
				bill.pay_bill()
				logger.info("Bill %s marked as paid." % bill.name)
			else:
				logger.info('Bill not paid.')
				continue
	core.all_bills_to_json()


if __name__ == '__main__':
	startup()
