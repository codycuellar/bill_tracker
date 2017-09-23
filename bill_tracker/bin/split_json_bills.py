import os
import json
from bill_tracker import core

core.load_bills()

os.chdir(os.path.dirname(__file__))
os.chdir('../../data/bills')


for bill in core.current_bills:
    filepath = os.path.join(os.getcwd(), bill.name + '.json')
    j = bill.to_json()
    with open(filepath, 'w') as f:
        json.dump(j, f, indent=4, sort_keys=True)
