#! /usr/bin/env python
import core

if __name__ == '__main__':
    core.load_json()
    core.check_due_dates()
    core.all_bills_to_json()
    core.send_email()
