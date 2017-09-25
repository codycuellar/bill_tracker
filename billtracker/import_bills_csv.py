import os
import core
import csv


def csv_to_dict(csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            core.current_bills.append(core.Bill(**row))


csv_file = os.path.join(core.data_dir, 'bills.csv')
csv_to_dict(csv_file)
core.all_bills_to_json()
