import os
import json
from datetime import datetime as dt
from datetime import timedelta
from email.mime.text import MIMEText
import config as cfg
import logging


logger = logging.getLogger(__name__)


current_bills = []


def load_bills():
    json_path = os.path.join(cfg.data_dir, 'bills')
    json_files = [j for j in os.listdir(json_path) if j.endswith('.json')]
    for j in json_files:
        logger.info('loading JSON file %s' % cfg.json_db_path)
        with open(j, 'r') as json_data:
            bill = json.load(json_data)
        logger.debug(bill)
        current_bills.append(Bill(**bill))
    Bill.categories.sort()


def all_bills_to_json():
    db_dict = []
    for bill in current_bills:
        db_dict.append(bill.to_json())
    with open(cfg.json_db_path, 'w') as json_data:
        json.dump(db_dict, json_data)


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
        elif bill.paid and bill.due_date in bill.past_three_days:
            recently_paid += formatted
    body = 'Total amount due in next two weeks: $%s\n\n' \
           'BILLS DUE:\n%s\n\n' \
           'BILLS OVERDUE:\n%s\n\n' \
           'BILLS RECENTLY PAID:\n%s\n\n' % \
           (round(Bill.current_outstanding_total, 2), bills_due,
            bills_past_due, recently_paid)
    date = dt.today()
    header = 'From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n' % (
        'noreply@gmail.com', ', '.join(cfg.email_to_addresses),
        ('%s Bill Updates $%s - %s' % (
            cfg.email_title, Bill.current_outstanding_total,
            date.strftime('%m-%d-%Y'))))
    msg = header + MIMEText(body).as_string()

    if DEBUG:
        logger.debug(msg)
    else:
        cfg.email_server.ehlo()
        cfg.email_server.starttls()
        with open(cfg.email_pw_path, 'r') as f:
            password = f.read()
        password = password[::-1]
        cfg.email_server.login(cfg.email_from_address, password)
        cfg.email_server.sendmail(cfg.email_from_address,
                                  cfg.email_to_addresses, msg)
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
        today = dt.today()
        logger.debug('Today is: %s' % today)
        for x in range(1, 15):
            cls.next_two_weeks.append((today + timedelta(x)).date())
        next_two_weeks_str = cls.dates_to_str(cls.next_two_weeks)
        logger.debug('Next two weeks: %s' % next_two_weeks_str)
        for x in range(3):
            cls.past_three_days.append((today - timedelta(x)).date())
        past_three_days = cls.dates_to_str(cls.past_three_days)
        logger.debug('Past three days: %s' % past_three_days)

    def __init__(self, name, category, bill_account_type, account_number,
                 automatic, due_date, due_day, due_month, due_year, due, paid,
                 overdue, variable_amount, bill_amount, amount_due,
                 outstanding_balance):
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
        self.due_date = dt.strptime(due_date, "%Y-%m-%d").date()
        self.due = due  # True if due in 2 weeks
        self.paid = paid  # Needs manually updated unless 'automatic' is False
        self.overdue = overdue  # For manual bills only
        self.outstanding_balance = outstanding_balance # For credit cards and loans
        Bill.categories.append(self.category)

    # def _load_csv(self, **kwargs):
    #     """Load the CSV file into objects."""
    #     for key in kwargs:
    #         if key in ['automatic', 'variable_amount']:
    #             if kwargs[key] == "True":
    #                 kwargs[key] = True
    #             else:
    #                 kwargs[key] = False
    #         elif key in ['amount_due', 'outstanding_balance', 'bill_amount']:
    #             if kwargs[key]:
    #                 kwargs[key] = float(kwargs[key])
    #             else:
    #                 continue
    #         elif key == 'due_year':
    #             if kwargs[key] == '*':
    #                 kwargs[key] = range(2017, 2050, 1)
    #         elif key == 'due_month':
    #             if kwargs[key] == '*':
    #                 kwargs[key] = range(1, 13)
    #             else:
    #                 kwargs[key] = [int(x) for x in kwargs[key].split(',')]
    #                 if len(kwargs[key]) > 1:
    #                     start, n = kwargs[key]
    #                     kwargs[key] = range(start, 13, n)
    #         elif key in ['account_number', 'due_day']:
    #             kwargs[key] = int(kwargs[key])
    #         elif key == 'category':
    #             if kwargs[key] not in Bill.categories:
    #                 Bill.categories.append(kwargs[key])
    #         self.__setattr__(key, kwargs[key])
    #     pass

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
        d= self.__dict__.copy()
        if d['due_date']:
            d['due_date'] = d['due_date'].strftime('%Y-%m-%d')
        json_dict = json.dumps(d, indent=4, sort_keys=True,
                               separators=(',', ':'))
        return json_dict

    def pay_bill(self):
        """Pay manual bills"""
        logger.info('Paying bill %s' % self.name)
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
        self.paid = True
        self.due = False
        self.overdue = False
        status = self.get_status_as_str()
        logger.debug(status)

    def set_due(self):
        self.due = True
        self.paid = False

    def get_status_as_str(self):
        return 'Status for %s: Automatic: %s - Amount Due: %s - Due ' \
               'Date: %s - Due: %s - Paid: %s - Overdue: %s' % (
                self.name, self.automatic, self.amount_due, self.due_date,
                self.due, self.paid, self.overdue)

    def set_status(self):
        """
        This function first updates the due day if it's in the next two weeks.
        :return: 
        """
        # Set the next due date
        for day in self.next_two_weeks:
            if (    day.year in self.due_year and
                    day.month in self.due_month and
                    day.day == self.due_day):
                logger.info('%s is in next two weeks on %s' % (self.name, day))
                self.due_date = day  # datetime object
                break

        if self.due_date in self.next_two_weeks:  # all automatic bills
            if self.automatic:
                logger.info('Setting bill %s as due on %s' % (self.name,
                                                              self.due_date))
                self.due = True
                self.paid = False
                self.amount_due = self.bill_amount
            elif not self.automatic and not self.paid:  # unpaid manual bill
                self.due = True
                self.amount_due = self.bill_amount
            else:
                self.due = False
            status = self.get_status_as_str()
            logger.debug(status)

        # Set attributes for paid / past-due bills
        elif self.due_date in self.past_three_days:
            logger.info('Bill %s in past three days: %s' % (
                self.name, self.due_date))
            if self.automatic:  # for auto-pay bills
                self.pay_bill()
        elif self.automatic:  # automatic bills
            logger.info('Removing automatic bill %s from past_three_days' %
                         self.name)
            self.mark_paid()
        elif not self.automatic and self.due:  # manual bills
            logger.info('Manual bill %s still due.' % self.name)
            self.overdue = True
            status = self.get_status_as_str()
            logger.debug(status)

