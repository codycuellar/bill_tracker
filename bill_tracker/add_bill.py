import core


def category_print():
    print "\nThese are the current categories available. Enter a new name to " \
          "add a new category."
    for category in core.Bills.categories:
        print category
    while True:
        usr_input = raw_input('\nCategory: ')
        if usr_input in core.Bills.categories:
            return usr_input
        else:
            print "\nDo you want to add '%s' as a new category? (y/n)" % \
                  usr_input
            if raw_input() in ['y', 'yes', '']:
                core.Bills.categories.append(usr_input)
                return usr_input
            else:
                '\nPlease enter a new category.'
                continue


def two_choices(return_val_1, return_val_2):
    while True:
        usr_input = raw_input('>>')
        if usr_input == '1':
            print "Set to '%s'" % return_val_1
            return return_val_1
        elif usr_input == '2':
            print "Set to '%s'" % return_val_2
            return return_val_2
        else:
            print '\nNot a valid entry, please enter 1 or 2.'
            continue


def set_frequency():
    print '\nWhat is the frequency of the bill? Enter 1 for monthly, ' \
          '2 for annually.'
    two_choices('monthly', 'annually')


def set_automatic():
    print '\nIs the bill set for auto-pay? (1 for yes, 2 for no):'
    two_choices(True, False)


def set_due_date():
    print '\nFor monthly bills, enter just the day of the month (DD), ' \
          'or for annual bills, enter the month and day (MM-DD). '
    while True:
        usr_input = raw_input('>>')
        input_list = usr_input.split('-')
        if all(isinstance(item, int) for item in input_list) is int and \
                len(input_list) in [2, 4]:
            return usr_input
        else:
            print '\nNot a valid entry, please try again.'
            continue


if __name__ == '__main__':

    obj_dict = {'name': raw_input('\nName: '),
                'category': category_print(),
                'bill_account_type': raw_input('\nBilling Account Type: '),
                'account_number': raw_input('\nAccount #: '),
                'frequency': set_frequency(),
                'due_date': set_due_date(),
                'automatic': set_automatic(),
                'amount': raw_input('\nBill amount: $').replace(',', ''),
                }

    core.current_bills.append(core.Bills(**obj_dict))