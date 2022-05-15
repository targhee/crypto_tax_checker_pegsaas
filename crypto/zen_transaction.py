import csv
import codecs
import datetime
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
			continue
		tx_counter += 1
		#print("\tAnalyzing trade: " + str(tx_counter))
		logging.debug("\tAnalyzing trade: " + str(tx_counter))
		#date = datetime.datetime.strptime(row[zen_timestamp], "%Y-%m-%dT%H:%M:%S%z")
		#print(f"Time Format: {row[zen_timestamp]}")
		#date = datetime.fromisoformat(str(row[zen_timestamp]))
		date = datetime.datetime.fromisoformat(str(row[zen_timestamp]))
		timestamp = date.strftime("%Y-%m-%d %H:%M:%S")
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
	return zen_transactions
