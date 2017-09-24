import os
import json
from bill_tracker import core
from bill_tracker import config as cfg


current_bills = []

core.Bill.update_calendar()

with open(cfg.json_db_path, 'r') as json_data:
    bills_dict = json.load(json_data)

for bill in bills_dict:
    bill['next_due_date'] = None
    del bill['due_date']
    bill = core.Bill(**bill)
    bill.due = False
    bill.paid = False
    bill.overdue = False
    bill.set_status()
    current_bills.append(bill)




os.chdir(os.path.join(os.path.dirname(cfg.json_db_path), 'bills'))


for bill in current_bills:
    filepath = os.path.join(os.getcwd(), bill.name + '.json')
    j = bill.to_json()
    with open(filepath, 'w') as f:
        f.write(j)
