import unittest
from unittest import TestCase
from bill_tracker import core
import json


class testBill(TestCase):
    def setUp(self):
        self.dict = {
            "account_number": 3760,
            "amount_due": 0.0,
            "automatic": False,
            "bill_account_type": "Check",
            "bill_amount": 384.6,
            "category": "Loan",
            "due": False,
            "due_date": "2017-10-01",
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
        self.json = json.dumps(self.dict, indent=4, sort_keys=True,
                               separators=(',', ':'))

    def test_Bill(self):
        bill_dict = json.loads(self.json)
        test_bill = core.Bill(**bill_dict)
        self.assertEqual(test_bill.to_json(), self.json)


if __name__ == '__main__':
    unittest.main()
