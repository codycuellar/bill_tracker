"""Rename this file to config.py when ready to run the script. Change all 
the variables below to reflect your setup."""


from os import path
import smtplib

data_dir = path.expanduser('PATH/TO/DIR')
json_db_path = path.join(data_dir, 'bills_db.json')
pw_file = path.join('PATH/TO/PW/FILE')

from_address = 'your@email.com'
to_addresses = [from_address, 'more@emails.com']
email_title = 'YOURLASTNAME'  # Name for email subject
server = smtplib.SMTP("smtp.someserver.com", PORT)  # set server and port #
