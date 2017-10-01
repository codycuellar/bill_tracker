import os
import json
import datetime as dt
from datetime import timedelta
from email.mime.text import MIMEText
import config as cfg
import logging


logger = logging.getLogger(__name__)


current_bills = []


def load_bills():
	json_path = os.path.join(cfg.data_dir, 'bills')
	logger.debug(json_path)
	json_files = [j for j in os.listdir(json_path) if j.endswith('.json')]
	for j in json_files:
		logger.info('loading JSON file %s' % j)
		with open(os.path.join(json_path, j), 'r') as json_data:
			bill = json.load(json_data)
		logger.debug(bill)
		current_bills.append(Bill(**bill))
	Bill.categories.sort()


def all_bills_to_json():
	json_path = os.path.join(cfg.data_dir, 'bills')
	for bill in current_bills:
		bill_name = bill.name + '.json'
		with open(os.path.join(json_path, bill_name), 'w') as f:
			f.write(bill.to_json())


def check_due_dates():
	Bill.update_calendar()
	for bill in current_bills:
		bill.set_status()
		if bill.due:
			Bill.current_outstanding_total += bill.amount_due


def send_email(DEBUG=False):
	bills_due = ''
	bills_past_due = ''
	recently_paid = ''
	for bill in current_bills:
		formatted = bill.format_for_email()
		if bill.due and not bill.overdue:
			bills_due += formatted
		elif bill.overdue:
			bills_past_due += formatted
		elif bill.paid:
			recently_paid += formatted
	body = 'Total amount due in next week: $%s\n\n' \
		   'BILLS DUE:\n%s\n\n' \
		   'BILLS OVERDUE:\n%s\n\n' \
		   'BILLS RECENTLY PAID:\n%s\n\n' % \
		   (round(Bill.current_outstanding_total, 2), bills_due,
			bills_past_due, recently_paid)
	date = dt.date.today()
	TEXT = MIMEText(body)
	TEXT['From'] = cfg.email_from_address
	TEXT['To'] = ','.join(cfg.email_to_addresses)
	TEXT['Subject'] = '%s Bill Updates $%s - %s' % (
			cfg.email_title, Bill.current_outstanding_total,
			date.strftime('%m-%d-%Y'))

	if DEBUG:
		logger.debug(TEXT.as_string())
	else:
		cfg.email_server.ehlo()
		cfg.email_server.starttls()
		with open(cfg.email_pw_path, 'r') as f:
			password = f.read()
		password = password[::-1]
		cfg.email_server.login(cfg.email_from_address, password)
		cfg.email_server.sendmail(cfg.email_from_address,
								  cfg.email_to_addresses,
								  TEXT.as_string())
		cfg.email_server.close()


class Bill(object):

	categories = []
	current_outstanding_total = 0.0
	billing_account_types = []
	next_two_weeks = []
	past_three_days = []

	@classmethod
	def dates_to_str(cls, dates):
		return [date.strftime('%m-%d-%Y') for date in dates]

	@classmethod
	def update_calendar(cls):
		today = dt.date.today()
		logger.debug('Today is: %s' % today)
		for day in range(1, 15):
			cls.next_two_weeks.append(today + timedelta(days=day))
		for day in range(3):
			cls.past_three_days.append(today - timedelta(day))

	def __init__(self, name, category, bill_account_type, account_number,
				 automatic, due_day, due_month, due_year, due, paid,
				 overdue, variable_amount, bill_amount, amount_due,
				 outstanding_balance, next_due_date):
		self.name = name
		self.category = category
		self.bill_account_type = bill_account_type
		self.account_number = account_number
		self.automatic = automatic
		self.due_year = due_year
		self.due_month = due_month
		self.due_day = due_day
		self.variable_amount = variable_amount
		self.bill_amount = bill_amount
		self.amount_due = amount_due
		self.due = due  # True if due in 2 weeks
		self.paid = paid  # Needs manually updated unless 'automatic' is False
		self.overdue = overdue  # For manual bills only
		self.outstanding_balance = outstanding_balance  # For credit cards
		# and loans
		Bill.categories.append(self.category)
		due_dates = []
		if next_due_date:
			self.next_due_date = dt.datetime.strptime(
				next_due_date, '%Y-%m-%d').date()
		else:
			for year in self.due_year:
				for month in self.due_month:
					if not isinstance(self.due_day, list):
						day = self.due_day
						# Avoid setting days outside of month (i.e. 30 in Feb)
						while True:
							try:
								due_dates.append(dt.date(year=year,
														 month=month,
														 day=day))
								break
							except ValueError:
								day -= 1
					else:
						for day in self.due_day:
							due_dates.append(
								dt.date(year=year, month=month, day=day))
			due_dates.sort()
			for date in due_dates:
				if date - dt.date.today() >= timedelta(days=0):
					self.next_due_date = date
					break

	def format_for_email(self):
		manual = ''
		if not self.automatic:
			manual = ' -- Manual'
		try:
			due_date = self.next_due_date.strftime('%b %d')
		except AttributeError:
			due_date = 'Unknown'
		return '\n\t%s - $%s (%s)%s' % (
			self.name, '{0:.2f}'.format(self.bill_amount),
			due_date, manual)

	def to_json(self):
		d = self.__dict__.copy()
		if d['next_due_date']:
			d['next_due_date'] = dt.datetime.strftime(
								 d['next_due_date'], '%Y-%m-%d')
		json_dict = json.dumps(d, indent=4, sort_keys=True,
							   separators=(',', ':'))
		return json_dict

	def pay_bill(self):
		"""Pay manual bills"""
		if self.outstanding_balance:
			logger.info('Subtracting outstanding balance.')
			self.outstanding_balance -= self.amount_due
			logger.debug('Outstanding balance for %s is %s' % (
				self.name, self.outstanding_balance))
		self.mark_paid()

	def mark_paid(self):
		"""Update the paid status of a bill."""
		logger.info('Marking bill %s as paid' % self.name)
		self.amount_due = 0.0
		self.due = False
		self.paid = True
		self.overdue = False
		status = self.get_status_as_str()
		logger.debug(status)

	def set_due(self):
		self.due = True
		self.paid = False
		self.amount_due = self.bill_amount

	def set_overdue(self):
		self.due = True
		self.paid = False
		self.overdue = True

	def clear_bill(self):
		self.due = False
		self.paid = False
		self.overdue = False
		self.next_due_date = None

	def get_status_as_str(self):
		return 'Status for %s: Automatic: %s - Amount Due: %s - Due ' \
			   'Date: %s - Due: %s - Paid: %s - Overdue: %s' % (
				self.name, self.automatic, self.amount_due, self.next_due_date,
				self.due, self.paid, self.overdue)

	def set_status(self):
		"""
		This function first updates the due day if it's in the next two weeks.
		:return: 
		"""
		if self.next_due_date in self.next_two_weeks:
			if self.automatic and not self.due or not self.paid \
					and not self.due:
				self.set_due()
			status = self.get_status_as_str()
			logger.debug(status)
			return

		# Set attributes for paid / past-due bills
		elif self.next_due_date in self.past_three_days:
			if self.automatic and not self.paid:  # for auto-pay bills
				self.pay_bill()
			elif not self.paid and not self.set_overdue():
				self.set_overdue()
			return

		else:
			if self.automatic or self.paid:
				self.clear_bill()

		status = self.get_status_as_str()
		logger.debug(status)
