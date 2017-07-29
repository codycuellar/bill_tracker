import os
import json
from datetime import timedelta
from datetime import datetime as dt
from email.mime.text import MIMEText
import config as cfg
import logging


logger = logging.getLogger(__name__)


__version__ = 'v1.0'


json_db_path = os.path.join(cfg.data_dir, 'bills_db.json')
current_bills = []


def load_json():
    with open(json_db_path, 'r') as json_data:
        bills_dict = json.load(json_data)
    for bill in bills_dict:
        current_bills.append(Bills(json_load=True, **bill))
    Bills.categories.sort()


def all_bills_to_json():
    db_dict = []
    for bill in current_bills:
        db_dict.append(bill.to_json())
    with open(json_db_path, 'w') as json_data:
        json.dump(db_dict, json_data)


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
        elif bill.paid and bill.due in bill.past_three_days:
            recently_paid += formatted
    body = 'Total amount due in next two weeks: $%s\n\n' \
           'BILLS DUE:\n%s\n\n' \
           'BILLS OVERDUE:\n%s\n\n' \
           'BILLS RECENTLY PAID:\n%s\n\n' % \
           (round(Bills.current_outstanding_total, 2), bills_due,
            bills_past_due, recently_paid)
    date = dt.today()
    header = 'From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n' % (
        'noreply@gmail.com', ', '.join(cfg.to_addresses),
        ('%s Bill Updates $%s - %s' % (
            cfg.email_title, Bills.current_outstanding_total,
            date.strftime('%m-%d-%Y'))))
    msg = header + MIMEText(body).as_string()

    if DEBUG:
        logger.debug(msg)
    else:
        cfg.email_server.ehlo()
        cfg.email_server.starttls()
        with open(cfg.pw_file, 'r') as f:
            password = f.read()
        password = password[::-1]
        cfg.email_server.login(cfg.from_address, password)
        cfg.email_server.sendmail(cfg.from_address, cfg.to_addresses, msg)
        cfg.email_server.close()


def check_due_dates():
    Bills.update_calendar()
    for bill in current_bills:
        bill.set_status()
        if bill.due:
            Bills.current_outstanding_total += bill.amount_due


class Bills(object):

    categories = []
    current_outstanding_total = 0.0
    billing_account_types = []
    next_two_weeks = []
    past_three_days = []

    @classmethod
    def update_calendar(cls):
        today = dt.today()
        for x in range(14):
            cls.next_two_weeks.append((today + timedelta(x)).date())
        for x in range(3):
            cls.past_three_days.append((today - timedelta(x)).date())

    def __init__(self, json_load=False, **kwargs):
        self.name = None
        self.category = None
        self.bill_account_type = None
        self.account_number = None
        self.automatic = False
        self.due_year = None
        self.due_month = None
        self.due_day = None
        self.variable_amount = False
        self.bill_amount = 0.0
        self.amount_due = 0.0
        self.due_date = None
        self.due = False  # True if due in 2 weeks
        self.paid = False  # Needs manually updated unless 'automatic' is False
        self.overdue = False  # For manual bills only
        self.outstanding_balance = 0.0  # For credit cards and loans
        if json_load:
            for attr in kwargs:
                if attr == 'due_date':
                    try:
                        kwargs[attr] = dt.strptime(kwargs[attr],
                                                   "%Y-%m-%d").date()
                    except TypeError:
                        pass
                setattr(self, attr, kwargs[attr])
        else:
            self._load_csv(**kwargs)

    def _load_csv(self, **kwargs):
        """Load the CSV file into objects."""
        for key in kwargs:
            if key in ['automatic', 'variable_amount']:
                if kwargs[key] == "True":
                    kwargs[key] = True
                else:
                    kwargs[key] = False
            elif key in ['amount_due', 'outstanding_balance', 'bill_amount']:
                if kwargs[key]:
                    kwargs[key] = float(kwargs[key])
                else:
                    continue
            elif key == 'due_year':
                if kwargs[key] == '*':
                    kwargs[key] = range(2017, 2050, 1)
            elif key == 'due_month':
                if kwargs[key] == '*':
                    kwargs[key] = range(1, 13)
                else:
                    kwargs[key] = [int(x) for x in kwargs[key].split(',')]
                    if len(kwargs[key]) > 1:
                        start, n = kwargs[key]
                        kwargs[key] = range(start, 13, n)
            elif key in ['account_number', 'due_day']:
                kwargs[key] = int(kwargs[key])
            elif key == 'category':
                if kwargs[key] not in Bills.categories:
                    Bills.categories.append(kwargs[key])
            self.__setattr__(key, kwargs[key])
        pass

    def format_for_email(self):
        manual = ''
        if not self.automatic:
            manual = ' -- Manual'
        try:
            due_date = self.due_date.strftime('%b %d')
        except:
            due_date = 'Unknown'
        return '\n\t%s - $%s (%s)%s' % (
            self.name, '{0:.2f}'.format(self.bill_amount),
            due_date, manual)

    def to_json(self):
        json = self.__dict__.copy()
        if json['due_date']:
            json['due_date'] = json['due_date'].strftime('%Y-%m-%d')
        return json

    def pay_bill(self):
        """Pay manual bills"""
        if self.outstanding_balance:
            self.outstanding_balance -= self.amount_due
        self.mark_paid()

    def mark_paid(self):
        """Update the paid status of a bill."""
        self.amount_due = 0.0
        self.paid = True
        self.due = False
        self.overdue = False

    def set_status(self):
        """
        This function first updates the due day if it's in the next two weeks.
        :return: 
        """
        # Set the due date if bill is due in next two weeks.
        for day in self.next_two_weeks:
            if (    day.year in self.due_year and
                    day.month in self.due_month and
                    day.day == self.due_day):
                self.due_date = day  # datetime object

        # Set attributes for next two weeks
        if self.due_date in self.next_two_weeks:  # all automatic bills
            if self.automatic:
                self.due = True
                self.paid = False
                self.amount_due = self.bill_amount
            elif not self.automatic and not self.paid:  # unpaid manual bill
                self.due = True
                self.amount_due = self.bill_amount
            else:
                self.due = False
        # Set attributes for paid / past-due bills
        elif self.due_date in self.past_three_days:
            if self.automatic:  # for auto-pay bills
                self.pay_bill()
        elif self.automatic:  # automatic bills
            self.mark_paid()
        elif not self.automatic and self.due:  # manual bills
            self.overdue = True
