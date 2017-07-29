#! /usr/bin/env python
import core
import logging

def main():
    core.load_json()
    core.check_due_dates()
    core.all_bills_to_json()
    core.send_email()

if __name__ == '__main__':
    logger = logging.getLogger()

    logger