import unittest

from beancount import loader
from beancount.parser import cmptest

from account_replacer import account_replacer


class TestAccountReplacer(cmptest.TestCase):

    @loader.load_doc(expect_errors=True)
    def test_ignore_replace_by_config(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:SomethingElse

        2013-05-31 * "Paid by card"
            Assets:Bank:Checking        -100 USD
            Expenses:SomethingElse       100 USD
        """
        config_str = ('{'
                      '"replace-rules":['
                      '{'
                      '"replace-from":"Expenses:Groceries",'
                      '"replace-to":"Expenses:Recurring:Groceries"'
                      '},'
                      '],'
                      '}')
        new_entries, _ = account_replacer(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 open Expenses:SomethingElse
        
        2013-05-31 * "Paid by card"
            Assets:Bank:Checking       -100 USD
            Expenses:SomethingElse      100 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_simple_replace_by_config(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Groceries

        2013-05-31 * "Paid by card"
            Assets:Bank:Checking        -100 USD
            Expenses:Groceries           100 USD
        """
        config_str = ('{'
                      '"replace-rules":['
                      '{'
                      '"replace-from":"Expenses:Groceries",'
                      '"replace-to":"Expenses:Recurring:Groceries"'
                      '},'
                      '],'
                      '}')
        new_entries, _ = account_replacer(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 open Expenses:Recurring:Groceries
        
        2013-05-31 * "Paid by card"
            Assets:Bank:Checking            -100 USD
            Expenses:Recurring:Groceries     100 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_deep_replace_by_config(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Groceries:Fruits
        2010-08-31 open Expenses:SomethingElse

        2013-05-31 * "Paid by card"
            Assets:Bank:Checking        -100 USD
            Expenses:Groceries:Fruits     20 USD
            Expenses:SomethingElse        80 USD
        """
        config_str = ('{'
                      '"replace-rules":['
                      '{'
                      '"replace-from":"Expenses:Groceries",'
                      '"replace-to":"Expenses:Recurring:Groceries"'
                      '},'
                      '],'
                      '}')
        new_entries, _ = account_replacer(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 open Expenses:Recurring:Groceries:Fruits
        2010-08-31 open Expenses:SomethingElse
        
        2013-05-31 * "Paid by card"
            Assets:Bank:Checking                   -100 USD
            Expenses:Recurring:Groceries:Fruits      20 USD
            Expenses:SomethingElse                   80 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_multi_postings_replace_and_ignore_by_config(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Groceries:Fruits
        2010-08-31 open Expenses:Groceries:Vegetables
        2010-08-31 open Expenses:Occasional:Groceries:Sweets

        2013-05-31 * "Paid by card"
            Assets:Bank:Checking                   -300 USD
            Expenses:Groceries:Fruits               100 USD
            Expenses:Groceries:Vegetables           100 USD
            Expenses:Occasional:Groceries:Sweets    100 USD
        """
        config_str = ('{'
                      '"replace-rules":['
                      '{'
                      '"replace-from":"Expenses:Groceries",'
                      '"replace-to":"Expenses:Recurring:Groceries"'
                      '},'
                      '],'
                      '}')
        new_entries, _ = account_replacer(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 open Expenses:Recurring:Groceries:Fruits
        2010-08-31 open Expenses:Recurring:Groceries:Vegetables
        2010-08-31 open Expenses:Occasional:Groceries:Sweets
        
        2013-05-31 * "Paid by card"
            Assets:Bank:Checking                       -300 USD
            Expenses:Recurring:Groceries:Fruits         100 USD
            Expenses:Recurring:Groceries:Vegetables     100 USD
            Expenses:Occasional:Groceries:Sweets        100 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_multi_rules_replace_by_config(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Groceries

        2013-05-31 * "Paid by card"
            Assets:Bank:Checking        -100 USD
            Expenses:Groceries           100 USD
        """
        config_str = ('{'
                      '"replace-rules":['
                      '{'
                      '"replace-from":"Expenses:Groceries",'
                      '"replace-to":"Expenses:Recurring:Groceries"'
                      '},'
                      '{'
                      '"replace-from":"Expenses:Other",'
                      '"replace-to":"Expenses:Recurring:Other"'
                      '},'
                      '],'
                      '}')
        new_entries, _ = account_replacer(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 open Expenses:Recurring:Groceries

        2013-05-31 * "Paid by card"
            Assets:Bank:Checking            -100 USD
            Expenses:Recurring:Groceries     100 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_pad_replace_by_config(self, entries, _, options_map):
        """
        2010-08-31 pad Assets:Bank:Checking Expenses:Groceries

        2013-05-31 * "Paid by card"
            Assets:Bank:Checking        -100 USD
            Expenses:Groceries           100 USD
        """
        config_str = ('{'
                      '"replace-rules":['
                      '{'
                      '"replace-from":"Expenses:Groceries",'
                      '"replace-to":"Expenses:Recurring:Groceries"'
                      '},'
                      '{'
                      '"replace-from":"Expenses:Other",'
                      '"replace-to":"Expenses:Recurring:Other"'
                      '},'
                      '],'
                      '}')
        new_entries, _ = account_replacer(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 pad Assets:Bank:Checking Expenses:Recurring:Groceries

        2013-05-31 * "Paid by card"
            Assets:Bank:Checking            -100 USD
            Expenses:Recurring:Groceries     100 USD
        """,
            new_entries,
        )


if __name__ == '__main__':
    unittest.main()
