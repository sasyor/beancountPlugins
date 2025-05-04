import unittest

from beancount import loader
from beancount.parser import cmptest

from entry_manipulation.entry_manipulators import entry_manipulators


class PostingConsolidatorOriginalPriceTest(cmptest.TestCase):
    @loader.load_doc(expect_errors=True)
    def test_original_price(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Bread

        2013-06-03 * "Purchase"
            Assets:Bank:Checking      -10 USD
            Expenses:Bread             10 USD
                original-price:        12 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-consolidator-original-price",'
                      '  "consolidate-price-account-postfix":"Price",'
                      '  "consolidate-discount-account-postfix":"Discount",'
                      '  "metadata-name-original-price":"original-price"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 open Expenses:Bread:Price
        2010-08-31 open Expenses:Bread:Discount

        2013-06-03 * "Purchase"
            Assets:Bank:Checking      -10 USD
            Expenses:Bread:Price       12 USD
            Expenses:Bread:Discount    -2 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_original_price_no_duplication(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Bread

        2013-06-03 * "Purchase"
            Assets:Bank:Checking      -10 USD
            Expenses:Bread             10 USD
                original-price:        12 USD

        2013-07-03 * "Purchase"
            Assets:Bank:Checking      -10 USD
            Expenses:Bread             10 USD
                original-price:        12 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-consolidator-original-price",'
                      '  "consolidate-price-account-postfix":"Price",'
                      '  "consolidate-discount-account-postfix":"Discount",'
                      '  "metadata-name-original-price":"original-price"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 open Expenses:Bread:Price
        2010-08-31 open Expenses:Bread:Discount

        2013-06-03 * "Purchase"
            Assets:Bank:Checking      -10 USD
            Expenses:Bread:Price       12 USD
            Expenses:Bread:Discount    -2 USD

        2013-07-03 * "Purchase"
            Assets:Bank:Checking      -10 USD
            Expenses:Bread:Price       12 USD
            Expenses:Bread:Discount    -2 USD
        """,
            new_entries,
        )


if __name__ == '__main__':
    unittest.main()
