import os
import logging
from django.conf import settings
from crypto.zen_transaction import process_zen_ledger
from crypto.cryptotax_functions import find_duplicated_transactions, find_paired_transactions4
from .models import Transaction

def remove_user_records(user):
    Transaction.objects.filter(user=user).delete()
    return

def load_and_parse_file(current_user, file_2_process):
    # Remove the User's previous records.
    remove_user_records(current_user)
    # Read in the Zen Ledger file.
    tx_class_list = process_zen_ledger(file_2_process)
    # Sort the transactions by timestamp
    transaction_list = sorted(
        list(tx_class_list),
        key=lambda o: o.timestamp)

    # Run some audits on the incoming transactions
    # A simple check for duplicated transactions
    duplicate_list, duplicate_string = find_duplicated_transactions(transaction_list)
    logging.debug("---------------------------------------------------------")
    logging.debug(duplicate_string)
    logging.debug("---------------------------------------------------------")
    logging.debug(f"Size of duplicates is {len(duplicate_list)}")
    for transaction in duplicate_list:
        logging.debug(f"Duplicate: {transaction}")

    transactions, matched_pairs, unmatched_tx, function_desc_string = \
        find_paired_transactions4(transaction_list)

    # with open("loader/files/sorted_transaction_list.csv", 'w') as sorted_file:
    # 	for transaction in transaction_list:
    # 		# print(transaction)
    # 		print(transaction, file=sorted_file)
    # print("---------------------------------------------------------")
    for transaction in transaction_list:
        t = Transaction(user=current_user, timestamp=transaction.timestamp,
                        trade_type=transaction.trade_type, in_asset=transaction.in_tx.asset,
                        in_qty=transaction.in_tx.qty, out_asset=transaction.out_tx.asset,
                        out_qty=transaction.out_tx.qty, fee_asset=transaction.fee.asset,
                        fee_qty=transaction.fee.qty, tx_id=transaction.tx_id,
                        exchange=transaction.exchange, part=transaction.part,
                        reconciled=transaction.reconciled, match_num=transaction.match_num,
                        duplicate=transaction.duplicate)
        t.save()
    return True

