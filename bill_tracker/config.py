from os import path
import time
import smtplib
import logging

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# BASIC
# -----------------------------------------------------------------------------
data_dir = path.expanduser('~/data')
json_db_path = path.join(data_dir, 'bills_db.json')
pw_file = path.join('password.txt')  # needs overridden in config_local


# -----------------------------------------------------------------------------
# EMAIL
# -----------------------------------------------------------------------------
from_address = 'your@email.com'
to_addresses = [from_address]
email_title = 'User'  # Name for email subject
email_server = smtplib.SMTP("smtp.gmail.com", 587)


# -----------------------------------------------------------------------------
# DB
# -----------------------------------------------------------------------------
db_name = 'billdb'
db_user = 'billuser'
db_hostname = 'localhost'
db_pw = 'pwfile'


# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
def configure_logging(logger, log_level=logging.WARNING,
                      file_level=logging.WARNING, console_level=logging.DEBUG,
                      logname=None):
    logger.setLevel(log_level)

    # Setup file logging
    date = time.strftime('%Y%m%d')
    if not logname:
        logname = logger.name
    logfile = '%s_%s.log' % (date, logname)
    logpath = path.join(data_dir, 'logs', logfile)

    file_handler = logging.FileHandler(logpath)
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter(
        '%(asctime)s:%(name)s:%(levelname)s: %(message)s')
    file_handler.setFormatter(file_formatter)

    # Setup Console logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


try:
    from config_local import *
except:
    logger.error('Could not load local configs. Program may not work.')
