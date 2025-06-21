import unittest

from beancount import loader
from beancount.core import data
from beancount.parser import cmptest

from entry_manipulation.entry_manipulators import entry_manipulators

manipulator_type = "posting-consolidator-discounter"


class PostingConsolidatorDiscounterTest(cmptest.TestCase):
    @loader.load_doc(expect_errors=True)
    def test_no_consolidation(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Bread

        2013-06-03 * "Purchase"
            Assets:Bank:Checking      -10 USD
            Expenses:Bread             10 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      f'  "type":"{manipulator_type}",'
                      '  "consolidate-price-account-postfix":"Price",'
                      '  "consolidate-discount-account-postfix":"Discount",'
                      '  "metadata-name-original-price":"original-price"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 open Expenses:Bread

        2013-06-03 * "Purchase"
            Assets:Bank:Checking      -10 USD
            Expenses:Bread             10 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_discount(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Cleaning:Washing:Detergent:Ariel

        2013-06-03 * "Purchase"
            Assets:Bank:Checking                       -3,999 HUF
            Expenses:Cleaning:Washing:Detergent:Ariel    2.15 L_DETERGENT {(4,999-1,000)/2.15 HUF}
                spar-coupons-discount-amount:           1,000 HUF
        """
        config_str = ('{"manipulators": ['
                      '{'
                      f'  "type":"{manipulator_type}",'
                      '  "consolidate-price-account-postfix":"Price",'
                      '  "consolidate-discount-account-postfix":"Spar:Coupons",'
                      '  "metadata-name-discount":"spar-coupons-discount-amount"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 open Expenses:Cleaning:Washing:Detergent:Ariel:Price
        2010-08-31 open Expenses:Cleaning:Washing:Detergent:Ariel:Spar:Coupons

        2013-06-03 * "Purchase"
            Assets:Bank:Checking                                    -3,999 HUF
            Expenses:Cleaning:Washing:Detergent:Ariel:Price           2.15 L_DETERGENT {(4,999-1,000)/2.15 HUF}
            Expenses:Cleaning:Washing:Detergent:Ariel:Price          1,000 HUF
            Expenses:Cleaning:Washing:Detergent:Ariel:Spar:Coupons  -1,000 HUF
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_original_price_no_duplication(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Cleaning:Washing:Detergent:Ariel

        2013-06-03 * "Purchase"
            Assets:Bank:Checking                       -3,999 HUF
            Expenses:Cleaning:Washing:Detergent:Ariel    2.15 L_DETERGENT {(4,999-1,000)/2.15 HUF}
                spar-coupons-discount-amount:           1,000 HUF

        2013-07-03 * "Purchase"
            Assets:Bank:Checking                       -3,999 HUF
            Expenses:Cleaning:Washing:Detergent:Ariel    2.15 L_DETERGENT {(4,999-1,000)/2.15 HUF}
                spar-coupons-discount-amount:           1,000 HUF
        """
        config_str = ('{"manipulators": ['
                      '{'
                      f'  "type":"{manipulator_type}",'
                      '  "consolidate-price-account-postfix":"Price",'
                      '  "consolidate-discount-account-postfix":"Spar:Coupons",'
                      '  "metadata-name-discount":"spar-coupons-discount-amount"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 open Expenses:Cleaning:Washing:Detergent:Ariel:Price
        2010-08-31 open Expenses:Cleaning:Washing:Detergent:Ariel:Spar:Coupons

        2013-06-03 * "Purchase"
            Assets:Bank:Checking                                    -3,999 HUF
            Expenses:Cleaning:Washing:Detergent:Ariel:Price           2.15 L_DETERGENT {(4,999-1,000)/2.15 HUF}
            Expenses:Cleaning:Washing:Detergent:Ariel:Price          1,000 HUF
            Expenses:Cleaning:Washing:Detergent:Ariel:Spar:Coupons  -1,000 HUF

        2013-07-03 * "Purchase"
            Assets:Bank:Checking                                    -3,999 HUF
            Expenses:Cleaning:Washing:Detergent:Ariel:Price           2.15 L_DETERGENT {(4,999-1,000)/2.15 HUF}
            Expenses:Cleaning:Washing:Detergent:Ariel:Price          1,000 HUF
            Expenses:Cleaning:Washing:Detergent:Ariel:Spar:Coupons  -1,000 HUF
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_remove_metadata(self, entries, _, options_map):
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

        for entry in new_entries:
            if isinstance(entry, data.Transaction):
                for posting in entry.postings:
                    if posting.meta:
                        self.assertIsNone(posting.meta.get('original-price'))


if __name__ == '__main__':
    unittest.main()
