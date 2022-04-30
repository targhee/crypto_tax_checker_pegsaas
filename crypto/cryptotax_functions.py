import sys
import os
import csv
import copy
import datetime
from crypto.cryptotax import CryptoTaxMatch

def populate_transaction_types(transactions):
	purchases = []
	sales = []
	for tx in transactions:
		print("-------------------------------------------------")
		print(f"TX: {tx}")
		if (tx.get_trade_type() == "buy") or (tx.get_trade_type() == "Receive"):
			print(f"Purchase: {tx}")
			purchases.append(tx)
		elif (tx.get_trade_type() == "sell") or (tx.get_trade_type() == "Send"):
			print(f"Sale: {tx}")
			sales.append(tx)
	print("-------------------------------------------------")
	return purchases, sales

def reconcile_transactions(purchases, sales) :
	tax_match = []
	# First, pair up purchases with each sale.
	for sell_tx in sales:
		print("--------------------------------------------------------------------------------------")
		#sell_tx.set_reconciled(False)
		#if sell_tx.get_reconciled() != None :
		# sell_tx_reconc = sell_tx.get_reconciled()
		if sell_tx.get_reconciled():
			continue
		# print("Transaction: " + str(sell_tx.get_ttype()) + " occurred on " + str(sell_tx.get_timestamp()) +
		# 	" to " + str(sell_tx.get_ttype()) + " " + str(sell_tx.get_qty()) + " of " +
		# 	str(sell_tx.get_asset()) + " for " + str((float(sell_tx.get_qty()) *
		# 	float(sell_tx.get_spot_price()))) + "[" + str(float(sell_tx.get_basis())) + "] " +
		# 	" | Reconciled: " + sell_tx_reconc)
		print(f"Sell Transaction: {sell_tx}")

		match_qty = sell_tx.get_out_qty()

		index = 0
		for buy_tx in list(purchases):
			if not buy_tx.get_reconciled():
				if match_qty <= 0 : # We've matched this transaction.
					sell_tx.set_reconciled(True)
					buy_tx.set_reconciled(True)
					tax_match.append(buy_tx)
					break
				#if not buy_tx.get_reconciled():
				#	buy_tx.set_reconciled("No")
				print("Index is " + str(index))
				# print("Transaction: " + str(buy_tx.get_ttype()) + " occurred on " + str(buy_tx.get_timestamp()) +
				# 	" to " + str(buy_tx.get_ttype()) + " " + str(buy_tx.get_qty()) + " of " +
				# 	str(buy_tx.get_asset()) + " for " + str((float(buy_tx.get_qty()) *
				# 	float(buy_tx.get_spot_price()))) + "[" + str(float(buy_tx.get_basis())) + "] " +
				# 	" | Reconciled: " + buy_tx.get_reconciled())
				print(f"Buy Transaction: {buy_tx}")
				# Buy transaction ammount completely consumed.
				if buy_tx.get_in_qty() <= match_qty:
					buy_tx.set_reconciled(True)
					match_qty = match_qty - buy_tx.get_in_qty()
					buy_tx.set_reconciled(True)
					tax_match.append(buy_tx)
				else:	# Special case, buy_qty more than needed, so
					# need to split this transaction into 2.
					original_tx = copy.deepcopy(buy_tx)
					new_tx = copy.deepcopy(buy_tx)
					parts = original_tx.get_part()
					print("Need to duplicate the buy_tx")
					# create new transaction that fulfills the sell tx.
					new_tx.set_in_qty(match_qty)
					# Since splitting, set new basis
					#new_tx.set_basis(original_tx.get_spot_price() * new_tx.get_qty())
					new_tx.set_out_qty((original_tx.get_out_qty() * new_tx.get_in_qty())/original_tx.get_in_qty())
					# on first partition, start at 1.
					if (int(new_tx.get_part()) == 0) : new_tx.set_part(1)
					new_tx.set_reconciled(True)
					tax_match.append(new_tx)
					# Update the current transaction to match what is leftover.
					buy_tx.set_in_qty(original_tx.get_in_qty() - match_qty)
					#buy_tx.set_basis(original_tx.get_basis() - new_tx.get_basis())
					buy_tx.set_out_qty(original_tx.get_out_qty() - new_tx.get_out_qty())
					buy_tx.set_part(int(new_tx.get_part()) + 1)
					# Remove the matched qty (isn't this 0?)
					match_qty = match_qty - new_tx.get_in_qty()
					# insert the new tx before current one.
					#purchases.insert(index, new_tx)
					print("Index is " + str(index))
					# print("New Transaction: " + str(new_tx.get_ttype()) + " occurred on " + str(new_tx.get_timestamp()) +
					# 	" to " + str(new_tx.get_ttype()) + " " + str(new_tx.get_qty()) + " of " +
					# 	str(new_tx.get_asset()) + " for " + str((float(new_tx.get_qty()) *
					# 	float(new_tx.get_spot_price()))) + "[" + str(float(new_tx.get_basis())) + "] " +
					# 	" | Reconciled: " + new_tx.get_reconciled() + " | " + str(new_tx.get_part()) +
					# 	" | " + new_tx.get_notes())
					# print("Current Transaction: " + str(buy_tx.get_ttype()) + " occurred on " + str(buy_tx.get_timestamp()) +
					# 	" to " + str(buy_tx.get_ttype()) + " " + str(buy_tx.get_qty()) + " of " +
					# 	str(buy_tx.get_asset()) + " for " + str((float(buy_tx.get_qty()) *
					# 	float(buy_tx.get_spot_price()))) + "[" + str(float(buy_tx.get_basis())) + "] " +
					# 	" | Reconciled: " + buy_tx.get_reconciled() + " | " + str(buy_tx.get_part()) +
					# 	" | " +  buy_tx.get_notes())
					print(f"New Transaction: {new_tx}")
					print(f"Current Transaction: {buy_tx}")
					index = index + 1
				# Increment the index here.
			index = index + 1
	return tax_match

def print_queue(queue_to_print, header_text):
	print("\n--------------------------------------------------------------")
	print(str(header_text))
	print("---------------------")
	for trans in queue_to_print:
		trans_reconc = "No"
		if trans.get_reconciled() != None :
			trans_reconc = trans.get_reconciled()

		cost = float(trans.get_qty()) * float(trans.get_spot_price())

#		print("Transaction: " + str(trans.get_ttype()) + " occurred on " +
#			str(trans.get_timestamp()) + " to " + str(trans.get_ttype()) +
#			" " + str(trans.get_qty()) + " of " + str(trans.get_asset()) +
#			" for " + str(round(cost), 2) + "[" +
#			str(round(float(trans.get_basis()),2)) + "] " + " | Reconciled:" +
#			str(trans_reconc) + " | " + str(trans.get_part()) + " | " + trans.get_notes())
		print("Transaction: %s occurred on %s to %s %f of %s for %.2f [%.2f] | Reconciled:%s | %d | %s " % 
			(str(trans.get_ttype()), str(trans.get_timestamp()), str(trans.get_ttype()), trans.get_qty(),
			str(trans.get_asset()), cost, float(trans.get_basis()),
			str(trans_reconc), trans.get_part(), trans.get_notes()))
	print("\n--------------------------------------------------------------\n")

def find_unpaired_transactions(transactions):
	receive = []
	sent = []
	#transactions_copy = copy.deepcopy(transactions)
	for tx in transactions:
		print("-------------------------------------------------")
		# print(f"TX: {tx}")
		if (tx.get_trade_type() == "Send"):
			print(f"Send: {tx}")
			sent.append(tx)
		elif (tx.get_trade_type() == "Receive"):
			print(f"Sale: {tx}")
			receive.append(tx)
	print("-------------------------------------------------")
	print(f"RxItems={len(receive)}; SentItems={len(sent)}")
	print("-------------------------------------------------")
	matched_pairs = []
	matched_flag = False
	# Search through Receives and match up with Sends.
	for rx in receive:
		matched_flag = False
		# skip any reconciled transactions
		if rx.get_reconciled():
			continue
		for tx in sent:
			# skip any reconciled transactions
			if tx.get_reconciled() or matched_flag:
				continue
			# if (rx.get_in_asset() == 'ADA') and (tx.get_out_asset == 'ADA'):
			# 	print(f"RX abracadabra test = {rx}")
			# 	print(f"TX abracadabra test = {tx}")
			if rx.get_in_asset() == tx.get_out_asset():
				# Check quantities first
				if rx.get_in_qty() == tx.get_out_qty():
					# Very likely a match...
					rx_ts = datetime.datetime.fromisoformat(rx.get_timestamp())
					tx_ts = datetime.datetime.fromisoformat(tx.get_timestamp())
					if (rx_ts > tx_ts) and (rx_ts - tx_ts < datetime.timedelta(hours=12)):
						print("Yeehaw!! Match found!")
						rx.set_reconciled(True)
						tx.set_reconciled(True)
						tx.set_match_num(rx.get_tx_id())
						rx.set_match_num(tx.get_tx_id())
						match = {"tx": tx, "rx":rx}
						matched_pairs.append(match)
						matched_flag = True
						print(f"TX:{tx}\nRX:{rx}")
					elif (tx_ts > rx_ts) and \
						(tx_ts - rx_ts < datetime.timedelta(hours=12)):
						print("Yeehaw!! Match found!")
						rx.set_reconciled(True)
						tx.set_reconciled(True)
						tx.set_match_num(rx.get_tx_id())
						rx.set_match_num(tx.get_tx_id())
						match = {"tx": tx, "rx":rx}
						matched_pairs.append(match)
						matched_flag = True
						print(f"TX:{tx}\nRX:{rx}")
					else:
						print("Missed it by that much...")
						#print(f"RX:{rx}\nTX:{tx}")

	return sent, receive, matched_pairs

def find_paired_transactions2(transactions):
	#transactions_copy = copy.deepcopy(transactions)
	matched_pairs = []
	print("-------------------------------------------------")
	for counter, tx in enumerate(transactions):
		# print(f"TX: {tx}")
		if tx.get_reconciled():
			continue
		# When see a Send, check the next 10 transactions to find a match.
		if (tx.get_trade_type() == "Send"):
			# First search backwards (The receive could have been timestamped before send)
			index = counter-1
			rx = transactions_copy[index]
			while datetime.datetime.fromisoformat(tx.get_timestamp()) - \
					datetime.datetime.fromisoformat(rx.get_timestamp()) < datetime.timedelta(hours=48):
				if (not rx.get_reconciled()) and (rx.get_trade_type() == "Receive") and \
					(rx.get_in_asset() == tx.get_out_asset()):
					rx_qty = rx.get_in_qty()
					tx_qty = tx.get_out_qty()
					print(f"Looks Promising... rx:{rx_qty} & tx:{tx_qty}")
					if rx_qty == tx_qty:
						print("Yep!! Match found!")
						transactions_copy[counter].set_reconciled(True)
						transactions_copy[index].set_reconciled(True)
						transactions_copy[counter].set_match_num(rx.get_tx_id())
						transactions_copy[index].set_match_num(tx.get_tx_id())
						match = {"tx": tx, "rx": rx}
						matched_pairs.append(match)
						print(f"TX:{tx}\nRX:{rx}")
						break
				index -= 1
				rx = transactions_copy[index]
			if tx.get_reconciled():
				continue
			# Search forwards
			# Check for matching receives for the next transactions (or until 48 hours difference)
			index = counter+1
			rx = transactions_copy[index]
			while datetime.datetime.fromisoformat(rx.get_timestamp()) - \
				  datetime.datetime.fromisoformat(tx.get_timestamp()) < datetime.timedelta(hours=48):
				if (not rx.get_reconciled()) and (rx.get_trade_type() == "Receive") and \
				   (rx.get_in_asset() == tx.get_out_asset()):
					rx_qty = rx.get_in_qty()
					tx_qty = tx.get_out_qty()
					print(f"Looks Promising... rx:{rx_qty} & tx:{tx_qty}")
					if rx_qty == tx_qty:
						print("Yep!! Match found!")
						transactions_copy[counter].set_reconciled(True)
						transactions_copy[index].set_reconciled(True)
						transactions_copy[counter].set_match_num(rx.get_tx_id())
						transactions_copy[index].set_match_num(tx.get_tx_id())
						match = {"tx": tx, "rx": rx}
						matched_pairs.append(match)
						print(f"TX:{tx}\nRX:{rx}")
						break
				index += 1
				rx = transactions_copy[index]

	print("-------------------------------------------------")

	return matched_pairs

def find_paired_transactions3(transactions):
	transactions_copy = copy.deepcopy(transactions)
	matched_pairs = []
	print("-------------------------------------------------")
	for counter, tx in enumerate(transactions_copy):
		# print(f"TX: {tx}")
		#print(f"Moving on to next transaction")
		if tx.get_reconciled():
			continue
		# When see a Send, check the next 10 transactions to find a match.
		if (tx.get_trade_type() == "Send"):
			# Search forwards
			# Check for matching receives for the next transactions (or until 48 hours difference)
			index = counter+1
			rx = transactions_copy[index]
			while datetime.datetime.fromisoformat(rx.get_timestamp()) - \
					datetime.datetime.fromisoformat(tx.get_timestamp()) < datetime.timedelta(hours=48):
				if (not rx.get_reconciled()) and (rx.get_trade_type() == "Receive") and \
						(rx.get_in_asset() == tx.get_out_asset()):
					rx_qty = rx.get_in_qty()
					tx_qty = tx.get_out_qty()
					#print(f"Looks Promising... rx:{rx_qty} & tx:{tx_qty}")
					if rx_qty == tx_qty:
						print("Yep!! Match found!")
						transactions_copy[counter].set_reconciled(True)
						transactions_copy[index].set_reconciled(True)
						transactions_copy[counter].set_match_num(rx.get_tx_id())
						transactions_copy[index].set_match_num(tx.get_tx_id())
						match = {"tx": tx, "rx": rx}
						matched_pairs.append(match)
						print(f"TX:{tx}\nRX:{rx}")
						break
				index += 1
				rx = transactions_copy[index]
			# Then search backwards (The receive could have been timestamped before send)
			index = counter-1
			rx = transactions_copy[index]
			while datetime.datetime.fromisoformat(tx.get_timestamp()) - \
					datetime.datetime.fromisoformat(rx.get_timestamp()) < datetime.timedelta(hours=48):
				if (not rx.get_reconciled()) and (rx.get_trade_type() == "Receive") and \
						(rx.get_in_asset() == tx.get_out_asset()):
					rx_qty = rx.get_in_qty()
					tx_qty = tx.get_out_qty()
					#print(f"Looks Promising... rx:{rx_qty} & tx:{tx_qty}")
					if rx_qty == tx_qty:
						print("Yep!! Match found!")
						transactions_copy[counter].set_reconciled(True)
						transactions_copy[index].set_reconciled(True)
						transactions_copy[counter].set_match_num(rx.get_tx_id())
						transactions_copy[index].set_match_num(tx.get_tx_id())
						match = {"tx": tx, "rx": rx}
						matched_pairs.append(match)
						print(f"TX:{tx}\nRX:{rx}")
						break
				index -= 1
				rx = transactions_copy[index]
			if tx.get_reconciled():
				continue
	print("-------------------------------------------------")
	return matched_pairs

def find_paired_transactions4(transactions):
	#transactions_copy = copy.deepcopy(transactions)
	matched_pairs = []
	print("-------------------------------------------------")
	for counter, tx in enumerate(transactions):
		# print(f"TX: {tx}")
		#print(f"Moving on to next transaction")
		if tx.get_reconciled():
			continue
		# When see a Send, check the next 10 transactions to find a match.
		if (tx.get_trade_type() == "Send"):
			# Search forwards
			# Check for matching receives for the next transactions (or until 48 hours difference)
			index = counter+1
			rx = transactions[index]
			while datetime.datetime.fromisoformat(rx.get_timestamp()) - \
					datetime.datetime.fromisoformat(tx.get_timestamp()) < datetime.timedelta(hours=48):
				if (not rx.get_reconciled()) and (rx.get_trade_type() == "Receive") and \
						(rx.get_in_asset() == tx.get_out_asset()):
					rx_qty = rx.get_in_qty()
					tx_qty = tx.get_out_qty()
					#print(f"Looks Promising... rx:{rx_qty} & tx:{tx_qty}")
					if rx_qty == tx_qty:
						#print("Yep!! Match found!")
						tx.set_reconciled(True)
						rx.set_reconciled(True)
						tx.set_match_num(rx.get_tx_id())
						rx.set_match_num(tx.get_tx_id())
						match = {"tx": tx, "rx": rx}
						matched_pairs.append(match)
						#print(f"TX:{tx}\nRX:{rx}")
						break
				index += 1
				rx = transactions[index]
			# Then search backwards (The receive could have been timestamped before send)
			index = counter-1
			rx = transactions[index]
			while datetime.datetime.fromisoformat(tx.get_timestamp()) - \
					datetime.datetime.fromisoformat(rx.get_timestamp()) < datetime.timedelta(hours=48):
				if (not rx.get_reconciled()) and (rx.get_trade_type() == "Receive") and \
						(rx.get_in_asset() == tx.get_out_asset()):
					rx_qty = rx.get_in_qty()
					tx_qty = tx.get_out_qty()
					#print(f"Looks Promising... rx:{rx_qty} & tx:{tx_qty}")
					if rx_qty == tx_qty:
						#print("Yep!! Match found!")
						tx.set_reconciled(True)
						rx.set_reconciled(True)
						tx.set_match_num(rx.get_tx_id())
						rx.set_match_num(tx.get_tx_id())
						match = {"tx": tx, "rx": rx}
						matched_pairs.append(match)
						#print(f"TX:{tx}\nRX:{rx}")
						break
				index -= 1
				rx = transactions[index]
			if tx.get_reconciled():
				continue
	print("-------------------------------------------------")
	unmatched_tx = []
	for tx in transactions:
		if (tx.get_trade_type() == 'Send') and (tx.get_match_num() == 0):
			unmatched_tx.append(tx)
	#print(f"Unmatched length = {len(unmatched_tx)}")
	function_desc_string = "\n".join(
		[f"An inspection found {len(unmatched_tx)} 'Send' transactions could not be matched",
		 "    to a 'Receive' transaction.",
		 "The following reasons could explain this:\n",
		 "1. The coin was sent as payment to someone. In this case, the coin is correctly",
		 "   interpreted as a 'Sell' action.",
		 "2. The coin was sent to another exchange that the tax software was not aware of.",
		 "   In this case, upload the other exchange so the matching 'Receive' can be found.",
		 "3. The coin was sent to a wallet that you control. In this case, the wallet should",
		 "   be added or a manual transaction added so this will not be listed as a sale.",
		 "   Be careful using this because if the IRS audits you later and you don't have",
		 "   the wallet address or the wallet indicates the coin left the wallet within the",
		 "   tax year, you'll be liable for taxes and penalties.",
		 "   Remember, for most coins, the blockchain is a complete history of transactions",
		 "   that the IRS can verify against your claims."
		 ]
	)
	return transactions, matched_pairs, unmatched_tx, function_desc_string

def duplicate_transactions(transactions):
	duplicate_list = []
	last = CryptoTaxMatch()
	for transaction in transactions:
		if transaction == last:
			duplicate_list.append(transaction)
			transaction.duplicate = True
		last = transaction
	return duplicate_list

def find_duplicated_transactions(transactions):
	# convert to a set and see if same size.
	duplicate_list = duplicate_transactions(transactions)
	duplicate_len = len(duplicate_list)
	function_desc_string = ""
	if duplicate_len > 0:
		function_desc_string = "\n".join(
			[f"An inspection found some potential duplicates (same timestamp, asset, & quantity)",
			 "Transactions that are listed as 'exchange:Manual' are even more suspicious because",
			 "they may have been entered in manually by the owner who may have accidentally entered",
			 "the same transaction multiple times.",
			f"[Found {duplicate_len} duplicates]"])
	return duplicate_list, function_desc_string


# purchases = deque()
# sales = deque()
# all_trans = deque()
# tax_match = deque()
#
# populate_transaction_types(filename, purchases, sales, all_trans)
# print_queue(purchases, "Purchases")
#
# reconcile_transactions(purchases, sales, tax_match)
#
# print_queue(purchases, "Purchases After Reconciling")
#
# print_queue(sales, "Sales")

#print("Purchases:")i
#print(purchases)
#print("\n")
#print("Sales:")
#print(sales)
#print("\n")

#print("All Transactions")
#for trans in all_trans:
#	trans_reconc = "No"
#	if trans.get_reconciled() != None :
#		trans_reconc = trans.get_reconciled()

#	print("Transaction: " + str(trans.get_ttype()) + " occurred on " + str(trans.get_timestamp()) +
#		" to " + str(trans.get_ttype()) + " " + str(trans.get_qty()) + " of " + 
#		str(trans.get_asset()) + " for " + str((float(trans.get_qty()) *
#		float(trans.get_spot_price()))) + "[" + str(float(trans.get_basis())) + "] " +
#		":Transaction Reconciled: " + trans_reconc)



#all_trans.popleft()

#print(all_trans)


