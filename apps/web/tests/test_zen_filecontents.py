from django.test import SimpleTestCase

from crypto.zen_transaction import validate_datetime, validate_tradetype, validate_qty, \
        validate_asset, validate_exchange


class ValidateFileInputs(SimpleTestCase):

    def test_validate_datetime(self):
        self.assertTrue(validate_datetime('2021-04-13T13:30:48-05:00'))
        self.assertTrue(validate_datetime('2021-04-13'))
        self.assertFalse(validate_datetime('2021-04-13T13:30:48-05000'))

    def test_validate_tradetype(self):
        self.assertTrue(validate_tradetype('buy'))
        self.assertTrue(validate_tradetype('sell'))
        self.assertTrue(validate_tradetype('Send'))
        self.assertTrue(validate_tradetype('Receive'))
        self.assertTrue(validate_tradetype('misc_reward'))
        self.assertFalse(validate_tradetype('not-a-trade'))
        self.assertFalse(validate_tradetype('1.2345'))

    def test_validate_qty(self):
        self.assertTrue(validate_qty('1.2000'))
        self.assertTrue(validate_qty('1234.5678'))
        self.assertTrue(validate_qty('1234.5678890'))
        self.assertTrue(validate_qty('123456'))
        self.assertFalse(validate_qty('-12.3456'))
        self.assertFalse(validate_qty('Not-a-number'))

    def test_validate_asset(self):
        self.assertTrue(validate_asset('BTC'))
        self.assertTrue(validate_asset('USDC'))
        self.assertTrue(validate_asset('USD'))
        self.assertTrue(validate_asset('1INCH'))
        self.assertFalse(validate_asset('Not-a-number'))

    def test_validate_exchange(self):
        self.assertTrue(validate_exchange('Coinbase'))
        self.assertTrue(validate_exchange('Kraken'))
        self.assertTrue(validate_exchange('Not-a-number'))
        self.assertFalse(validate_exchange('1234567890123456789012345'))
