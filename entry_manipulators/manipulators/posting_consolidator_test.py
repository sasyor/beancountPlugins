import unittest

from beancount import loader
from beancount.parser import cmptest

from entry_manipulators.entry_manipulators import entry_manipulators


class PostingConsolidatorTest(cmptest.TestCase):
    @loader.load_doc(expect_errors=True)
    def test_consolidate(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Bread

        2013-06-03 * "Purchase"
            Assets:Bank:Checking      -10 USD
            Expenses:Bread             12 USD
            Expenses:Bread             -2 USD
                discount: "Discount"
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-consolidator",'
                      '  "consolidate-account-postfix":"Price",'
                      '  "metadata-name-consolidate-account-postfix":"discount"'
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
    def test_consolidate_rename(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Bread

        2013-06-03 * "Purchase"
            Assets:Bank:Checking      -10 USD
            Expenses:Bread             12 USD
            Expenses:Bread             -2 USD
                discount: "Discount"

        2013-07-03 * "Purchase"
            Assets:Bank:Checking      -12 USD
            Expenses:Bread             12 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-consolidator",'
                      '  "consolidate-account-postfix":"Price",'
                      '  "metadata-name-consolidate-account-postfix":"discount"'
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
            Assets:Bank:Checking      -12 USD
            Expenses:Bread:Price       12 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_consolidate_no_duplication(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Bread

        2013-06-03 * "Purchase"
            Assets:Bank:Checking      -10 USD
            Expenses:Bread             12 USD
            Expenses:Bread             -2 USD
                discount: "Discount"

        2013-07-03 * "Purchase"
            Assets:Bank:Checking      -10 USD
            Expenses:Bread             12 USD
            Expenses:Bread             -2 USD
                discount: "Discount"
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-consolidator",'
                      '  "consolidate-account-postfix":"Price",'
                      '  "metadata-name-consolidate-account-postfix":"discount"'
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
