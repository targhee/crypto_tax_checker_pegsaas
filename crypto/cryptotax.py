class CryptoTax:
	def __init__(self, timestamp=None, trade_type=None, in_asset=None, in_qty=None,
				 out_qty=None, out_asset=None, fee_currency=None, tx_fee=None,
				 tx_id=None, exchange=None, part=0):
		self.timestamp = timestamp
		self.trade_type = trade_type
		self.in_tx = self.CryptoTransaction(asset=in_asset, qty=in_qty)
		self.out_tx = self.CryptoTransaction(asset=out_asset, qty=out_qty)
		self.fee = self.CryptoTransaction(asset=fee_currency, qty=tx_fee)
		self.tx_id = tx_id
		self.exchange = exchange
		self.part = part

	class CryptoTransaction:
		def __init__(self, asset=None, qty=None):
			self.asset = asset
			self.qty = qty

		def __str__(self):
			return f"[asset:{self.asset};qty:{self.qty}]"

	def get_timestamp(self):
		return self.timestamp

	def get_trade_type(self):
		return self.trade_type

	def get_in_asset(self):
		return self.in_tx.asset

	def get_in_qty(self):
		return float(self.in_tx.qty)

	def get_out_asset(self):
		return self.out_tx.asset

	def get_out_qty(self):
		return float(self.out_tx.qty)

	def get_fee_asset(self):
		return self.fee.asset

	def get_tx_fee(self):
		return float(self.fee.qty)

	def get_tx_id(self):
		return self.tx_id

	def get_part(self):
		return int(self.part)

	def get_exchange(self):
		return str(self.exchange)

	def set_timestamp(self, timestamp=None):
		self.timestamp = timestamp

	def set_trade_type(self, trade_type=None):
		self.trade_type = trade_type

	def set_in_asset(self, in_asset=None):
		self.in_tx.asset = in_asset

	def set_in_qty(self, in_qty=None):
		self.in_tx.qty = float(in_qty)

	def set_out_asset(self, out_asset=None):
		self.out_tx.asset = out_asset

	def set_out_qty(self, out_qty=None):
		self.out_tx.qty = float(out_qty)

	def set_fee_currency(self, fee_currency=None):
		self.fee.asset = str(fee_currency)

	def set_tx_fee(self, tx_fee=None):
		self.fee.qty = float(tx_fee)

	def set_tx_id(self, tx_id=None):
		self.tx_id = tx_id

	def set_part(self, part=None):
		self.part = int(part)

	def set_exchange(self, exchange=None):
		self.exchange = str(exchange)

	def __str__(self):
		return ";".join([f"timestamp:{self.timestamp};tradetype:{self.trade_type}",
						f"in_tx:{self.in_tx};out_tx:{self.out_tx}",
						f"fee:{self.fee};tx_id:{self.tx_id}",
						f"exchange:{self.exchange};part:{self.part}"])

	def __eq__(self, second):
		return (self.timestamp == second.timestamp) and (self.trade_type == second.trade_type) and \
			   (self.in_tx.asset == second.in_tx.asset) and (self.in_tx.qty == second.in_tx.qty) and \
			   (self.out_tx.qty == second.out_tx.qty) and (self.out_tx.asset == second.out_tx.asset) and \
			   (self.fee.asset == second.fee.asset) and (self.fee.qty == second.fee.qty) and \
			   (self.exchange == second.exchange) and (self.part == second.part)

class CryptoTaxMatch(CryptoTax):

	def __init__(self, timestamp=None, trade_type=None, in_asset=None, in_qty=None,
				 out_qty=None, out_asset=None, fee_currency=None, tx_fee=None,
				 tx_id=None, exchange=None, part=0, reconciled=False, match_num=0,
				 duplicate=False):
		super().__init__(timestamp=timestamp, trade_type=trade_type, in_asset=in_asset,
						 in_qty=in_qty, out_qty=out_qty, out_asset=out_asset,
						 fee_currency=fee_currency, tx_fee=tx_fee, tx_id=tx_id,
						 exchange=exchange, part=part)
		self.reconciled = reconciled
		self.match_num = match_num
		self.duplicate = duplicate

	def get_reconciled(self):
		return self.reconciled

	def set_reconciled(self, reconciled=None):
		self.reconciled = reconciled

	def get_match_num(self):
		return self.match_num

	def set_match_num(self, match_num=0):
		self.match_num = match_num

	def get_dup(self):
		return self.duplicate

	def set_duplicate(self, duplicate=False):
		self.duplicate = duplicate

	def __str__(self):
		return ";".join([f"timestamp:{self.timestamp};tradetype:{self.trade_type}",
						 f"in_tx:{self.in_tx};out_tx:{self.out_tx}",
						 f"fee:{self.fee};tx_id:{self.tx_id}",
						 f"exchange:{self.exchange};part:{self.part}",
						 f"reconciled:{self.reconciled};match:{self.match_num}",
						 f"duplicate:{self.duplicate}"])

	def __eq__(self, second):
		return (self.timestamp == second.timestamp) and (self.trade_type == second.trade_type) and \
			   (self.in_tx.asset == second.in_tx.asset) and (self.in_tx.qty == second.in_tx.qty) and \
			   (self.out_tx.qty == second.out_tx.qty) and (self.out_tx.asset == second.out_tx.asset) and \
			   (self.fee.asset == second.fee.asset) and (self.fee.qty == second.fee.qty) and \
			   (self.exchange == second.exchange) and (self.part == second.part) and \
			   (self.reconciled == second.reconciled) and (self.match_num == second.match_num)
