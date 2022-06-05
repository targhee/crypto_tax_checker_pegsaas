import csv
import codecs
import datetime
import rfc3339      # for date object -> date string
import iso8601      # for date string -> date object
import sys
import logging
from crypto.cryptotax import CryptoTax, CryptoTaxMatch
from django.core.files.storage import default_storage

zen_timestamp = 0
zen_trade_type = 1
zen_in_qty = 2
zen_in_asset = 3
zen_out_qty = 4
zen_out_asset = 5
zen_fee_amount = 6
zen_fee_asset = 7
zen_exchange = 8
zen_us_based = 9
zen_txid = 10

def validate_datetime(datetime_to_check):
	if len(datetime_to_check) > 26:
		return False
	try:
		# Remove the last colon (need this to be -0400 instead of -04:00
		#datetime.datetime.strptime(datetime_to_check, "%Y-%m-%dT%H:%M:%S%z")
		iso8601.parse_date(datetime_to_check)
		return True
	except ValueError:
		return False

def validate_tradetype(trade_to_check):
	if len(trade_to_check) < 15:
		if (trade_to_check == 'buy' or
			trade_to_check =='sell' or
			trade_to_check == 'Send' or
			trade_to_check == 'Receive' or
			trade_to_check == 'misc_reward' or
			trade_to_check == 'staking_reward' or
			trade_to_check == 'trade' or
			trade_to_check == 'airdrop' or
			trade_to_check == 'fee'):
			return True
	return False

def validate_qty(qty_to_check):
	if len(qty_to_check) > 26:
		return False
	# This could be empty so we should handle this
	if not qty_to_check:
		return True
	# Check for all numbers except a decimal point
	if not qty_to_check.isnumeric():
		# Remove decimal point and check again.
		parts = qty_to_check.split(".")
		if len(parts) > 2:
			return False
		if not parts[0].isnumeric() or not parts[1].isnumeric():
			return False
	try:
		if float(qty_to_check) < 0:
			return False
	except ValueError:
		return False
	return True

def validate_asset(asset_to_check):
	# Check for valid asset length because it could be empty or have a number or --
	return  len(asset_to_check) < 8

def validate_exchange(exchange_to_check):
	return len(exchange_to_check) < 20

def validate_row(row):
	if not validate_datetime(str(row[zen_timestamp])):
		logging.error(f"This is the incorrect date string format. It should be YYYY-MM-DDTHH:MM:SS-HH:MM:\n {str(row[zen_timestamp])}")
		logging.error("\tFound an error validating Date-Time " + str(row[zen_timestamp]))
		return False
	if not validate_tradetype(str(row[zen_trade_type])):
		logging.error("\tFound an error validating Trade Type " + str(row[zen_trade_type]))
		return False
	if (not validate_qty(str(row[zen_in_qty])) or not validate_qty(str(row[zen_out_qty])) or
		not validate_qty(str(row[zen_fee_amount]))):
		logging.error(f"\tError validating Quantity: In:{str(row[zen_in_qty])}, Out:{str(row[zen_out_qty])}, Fee:{str(row[zen_fee_amount])}")
		return False
	if (not validate_asset(str(row[zen_in_asset])) or not validate_asset(str(row[zen_out_asset])) or
		not validate_asset(str(row[zen_fee_asset]))):
		logging.error(f"\tError validating Asset: In:{str(row[zen_in_asset])}; Out:{str(row[zen_out_asset])}; Fee:{str(row[zen_fee_asset])}")
		return False
	if not validate_exchange(str(row[zen_exchange])):
		logging.error(f"\tError validating Exchange: {str(row[zen_exchange])}")
		return False
	if len(str(row[zen_us_based])) > 4:
		logging.error(f"\tFound an error validating US Based: {str(row[zen_us_based])}")
		return False
	if len(str(row[zen_txid])) > 100:
		logging.error(f"\tFound an error validating TX ID: {str(row[zen_txid])}")
		return False
	return True

###################################################
# Coinbase #######  UTC
###################################################
# Format of the input Zen Ledger is
#   0         1        2           3           4            5            6          7                 8               9       10
# Timestamp, Type, IN Amount, IN Currency, Out Amount, Out Currency, Fee Amount, Fee Currency, Exchange(optional), US Based, Txid
# 2021-04-13T13:30:48-05:00,buy,166.3975206,NU,102.01,USD,2.98999999999999,USD,Coinbase,Yes,4f10b3bc-e4ea-5a91-a88a-805d0f6191dd
##################################################

def process_zen_ledger(filename):
	print("\nReading Zen Ledger - All Transactions")
	logging.debug("\nReading Zen Ledger - All Transactions")
	zen_transactions = list()
	tx_counter = 0
	csvreader = csv.reader(
		codecs.getreader('utf-8')(default_storage.open(filename, 'rb')),
		delimiter=',')
	header_key = "Timestamp"
	line = ""
	try:
		# Skip crap headers
		line = next(csvreader)
		while header_key not in line:
			line = next(csvreader)
	except csv.Error as e:
		sys.exit('file {}, line {}: {}'.format(filename, line.line_num, e))
	header = line
	print("Header: " + str(header))
	for row in csvreader:
		# Skip any empty rows.
		if not ''.join(row).strip():
			print("\tSkipping Row")
			continue
		tx_counter += 1
		if not validate_row(row):
			#logging.error("\tFound an error validating row[{tx_counter}]: " + str(row))
			print(f"Found an error validating row[{tx_counter}]")
			continue
		logging.debug("\tAnalyzing trade: " + str(tx_counter))
		#date = datetime.datetime.strptime(row[zen_timestamp], "%Y-%m-%dT%H:%M:%S%z")
		#print(f"Time Format: {row[zen_timestamp]}")
		#date = datetime.fromisoformat(str(row[zen_timestamp]))
		#date = datetime.datetime.fromisoformat(str(row[zen_timestamp]))
		newdate = iso8601.parse_date(str(row[zen_timestamp]))
		timestamp = newdate.strftime("%Y-%m-%d %H:%M:%S")
		trade_type = str(row[zen_trade_type])
		in_qty = str(row[zen_in_qty])
		# What does a blank in_qty mean? Think it means DeFi Exchange creation
		if not in_qty:
			in_qty = float(0.0)
		else:
			in_qty = float(in_qty)
		in_asset = str(row[zen_in_asset])
		out_qty = str(row[zen_out_qty])
		out_asset = str(row[zen_out_asset])
		# What does a blank out_qty mean? Seems to be for USD
		if not out_qty:
			out_qty = in_qty
			if not out_asset:
				out_asset = in_asset
		else:
			out_qty = float(out_qty)
		fee_currency = str(row[zen_fee_asset])
		tx_fee = str(row[zen_fee_amount])
		if tx_fee == "":
			tx_fee = "0"
		tx_id = str(row[zen_txid])
		# some of the tx_ids span multiple lines so remove \r\n whitespace
		tx_id = ''.join(tx_id.splitlines()).strip()
		exchange = str(row[zen_exchange])
		tax_element = CryptoTaxMatch(timestamp=timestamp, trade_type=trade_type,
									 in_asset=in_asset, in_qty=in_qty, out_asset=out_asset,
									 out_qty=out_qty, fee_currency=fee_currency,
									 tx_fee=tx_fee, tx_id=tx_id, exchange=exchange, part=0,
									 reconciled=False, match_num=0)
		zen_transactions.append(tax_element)
		#print(tax_element)
	print(f"\tAnalyzed {str(tx_counter)} transactions")
	return zen_transactions
