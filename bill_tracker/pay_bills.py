#! /usr/bin/env python
import core

if __name__ == '__main__':
    core.load_json()
    for bill in [b for b in core.current_bills if not b.automatic]:
        if bill.due:
            print '\nDid you pay', bill.name, '? (y/n)'
            response = raw_input("> ")
            if response.lower() in ['yes', 'y']:
                bill.pay_bill()
                print "Bill %s marked as paid." % bill.name
            else:
                print 'Bill not paid.'
                continue
    core.all_bills_to_json()
