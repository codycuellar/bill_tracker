import unittest
from unittest import TestCase
from bill_tracker import core
import datetime as dt
from datetime import timedelta as td
import json


class TestBill(TestCase):
	def setUp(self):
		core.Bill.update_calendar()
		self.bill_dict = {
			"account_number": 3760,
			"amount_due": 0.0,
			"automatic": False,
			"bill_account_type": "Check",
			"bill_amount": 384.6,
			"category": "Loan",
			"due": False,
			"next_due_date": None,
			"due_day": 1,
			"due_month": [
				1,
				2,
				3,
				4,
				5,
				6,
				7,
				8,
				9,
				10,
				11,
				12
			],
			"due_year": [
				2017,
				2018,
				2019,
				2020,
				2021,
				2022,
				2023,
				2024,
				2025,
				2026,
				2027,
				2028,
				2029,
				2030,
				2031,
				2032,
				2033,
				2034,
				2035,
				2036,
				2037,
				2038,
				2039,
				2040,
				2041,
				2042,
				2043,
				2044,
				2045,
				2046,
				2047,
				2048,
				2049
			],
			"name": "Wings (Cars)",
			"outstanding_balance": 13713.43,
			"overdue": False,
			"paid": True,
			"variable_amount": False}
		bill_dict = self.bill_dict.copy()
		self.bill_json = json.dumps(bill_dict, indent=4, sort_keys=True,
									separators=(',', ':'))
		self.bill = core.Bill(**bill_dict)

	def test_Bill_json(self):
		bill_dict = json.loads(self.bill_json)
		test_bill = core.Bill(**bill_dict)
		test_bill.next_due_date = None
		bill_dict['next_due_date'] = None
		self.assertEqual(test_bill.to_json(), self.bill_json)

	def test_automatic_cycle(self):
		core.Bill.update_calendar()
		bill = self.bill
		bill.automatic = True
		bill.due = False
		bill.paid = False
		bill.overdue = False

		for x in range(3):
			bill.next_due_date = dt.date.today() + td(days=15)
			self.assertFalse(bill.next_due_date in
							 bill.next_two_weeks)
			self.assertFalse(bill.next_due_date in
							 bill.past_three_days)
			bill.set_status()
			self.assertFalse(bill.due)
			self.assertFalse(bill.paid)
			self.assertFalse(bill.overdue)

			bill.next_due_date = dt.date.today() + td(days=14)
			self.assertTrue(bill.next_due_date in
							bill.next_two_weeks)
			self.assertFalse(bill.next_due_date in
							 bill.past_three_days)
			bill.set_status()
			self.assertTrue(bill.due)
			self.assertFalse(bill.paid)
			self.assertFalse(bill.overdue)

			bill.next_due_date = dt.date.today()
			self.assertFalse(bill.next_due_date in
							 bill.next_two_weeks)
			self.assertTrue(bill.next_due_date in
							bill.past_three_days)
			bill.set_status()
			self.assertFalse(bill.due)
			self.assertTrue(bill.paid)
			self.assertFalse(bill.overdue)

			bill.next_due_date = dt.date.today() - td(days=3)
			self.assertFalse(bill.next_due_date in
							 bill.next_two_weeks)
			self.assertFalse(bill.next_due_date in
							 bill.past_three_days)
			bill.set_status()
			self.assertFalse(bill.due)
			self.assertFalse(bill.paid)
			self.assertFalse(bill.overdue)

	def test_manual_cycle(self):
		core.Bill.update_calendar()
		bill = self.bill
		bill.automatic = False
		bill.due = False
		bill.paid = False
		bill.overdue = False

		# Test paid on time
		for x in range(2):
			bill.next_due_date = dt.date.today() + td(days=15)
			self.assertFalse(bill.next_due_date in
							 bill.next_two_weeks)
			self.assertFalse(bill.next_due_date in
							 bill.past_three_days)
			bill.set_status()
			self.assertFalse(bill.due)
			self.assertFalse(bill.paid)
			self.assertFalse(bill.overdue)

			bill.next_due_date = dt.date.today() + td(days=14)
			self.assertTrue(bill.next_due_date in
							bill.next_two_weeks)
			self.assertFalse(bill.next_due_date in
							 bill.past_three_days)
			bill.set_status()
			self.assertTrue(bill.due)
			self.assertFalse(bill.paid)
			self.assertFalse(bill.overdue)

			bill.pay_bill()
			self.assertFalse(bill.due)
			self.assertTrue(bill.paid)
			self.assertFalse(bill.overdue)

			bill.next_due_date = dt.date.today()
			self.assertFalse(bill.next_due_date in
							 bill.next_two_weeks)
			self.assertTrue(bill.next_due_date in
							bill.past_three_days)
			bill.set_status()
			self.assertFalse(bill.due)
			self.assertTrue(bill.paid)
			self.assertFalse(bill.overdue)

			bill.next_due_date = dt.date.today() - td(days=3)
			self.assertFalse(bill.next_due_date in
							 bill.next_two_weeks)
			self.assertFalse(bill.next_due_date in
							 bill.past_three_days)
			bill.set_status()
			self.assertFalse(bill.due)
			self.assertFalse(bill.paid)
			self.assertFalse(bill.overdue)

		# Test late payment
		bill.next_due_date = dt.date.today() + td(days=15)
		self.assertFalse(bill.next_due_date in
						 bill.next_two_weeks)
		self.assertFalse(bill.next_due_date in
						 bill.past_three_days)
		bill.set_status()
		self.assertFalse(bill.due)
		self.assertFalse(bill.paid)
		self.assertFalse(bill.overdue)

		bill.next_due_date = dt.date.today() + td(days=14)
		self.assertTrue(bill.next_due_date in
						bill.next_two_weeks)
		self.assertFalse(bill.next_due_date in
						 bill.past_three_days)
		bill.set_status()
		self.assertTrue(bill.due)
		self.assertFalse(bill.paid)
		self.assertFalse(bill.overdue)

		bill.next_due_date = dt.date.today()
		self.assertFalse(bill.next_due_date in
						 bill.next_two_weeks)
		self.assertTrue(bill.next_due_date in
						bill.past_three_days)
		bill.set_status()
		self.assertTrue(bill.due)
		self.assertFalse(bill.paid)
		self.assertTrue(bill.overdue)

		bill.next_due_date = dt.date.today() - td(days=3)
		self.assertFalse(bill.next_due_date in
						 bill.next_two_weeks)
		self.assertFalse(bill.next_due_date in
						 bill.past_three_days)
		bill.set_status()
		self.assertTrue(bill.due)
		self.assertFalse(bill.paid)
		self.assertTrue(bill.overdue)

		bill.pay_bill()
		self.assertFalse(bill.due)
		self.assertTrue(bill.paid)
		self.assertFalse(bill.overdue)

		bill.set_status()
		self.assertFalse(bill.due)
		self.assertFalse(bill.paid)
		self.assertFalse(bill.overdue)




if __name__ == '__main__':
	unittest.main()
