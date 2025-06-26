import unittest

from beancount import loader
from beancount.parser import cmptest

from entry_manipulation.entry_manipulators import entry_manipulators

manipulator_type = "posting-spreader"


class PostingConsolidatorSpreaderTest(cmptest.TestCase):
    @loader.load_doc(expect_errors=True)
    def test_spread_posting_to_metadata_account(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Hygiene:BarSoap

        2013-06-03 * "Purchase"
            Assets:Bank:Checking                       -8,154 HUF
            Expenses:Hygiene:BarSoap                  (2+4)*4 PCS_DOVE_BAR_SOAP {1,699/4 HUF}
            Expenses:Hygiene:BarSoap             -(680+1,360) HUF
                discount-account: "Tesco:Clubcard"
        """
        config_str = ('{"manipulators": ['
                      '{'
                      f'  "type":"{manipulator_type}",'
                      '  "roundings":{'
                      '      "USD":2'
                      '    },'
                      '  "consolidate-price-account-postfix":"Price",'
                      '  "spread-base":"unit",'
                      '  "match-mode":"same-account",'
                      '  "metadata-name-spread-account-postfix":"discount-account"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 open Expenses:Hygiene:BarSoap:Price
        2010-08-31 open Expenses:Hygiene:BarSoap:Tesco:Clubcard

        2013-06-03 * "Purchase"
            Assets:Bank:Checking                             -8,154 HUF
            Expenses:Hygiene:BarSoap:Price                  (2+4)*4 PCS_DOVE_BAR_SOAP {1,699/4-(680+1,360)/((2+4)*4) HUF}
            Expenses:Hygiene:BarSoap:Price              (680+1,360) HUF
            Expenses:Hygiene:BarSoap:Tesco:Clubcard    -(680+1,360) HUF
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_spread_posting_to_metadata_account_no_duplication(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Hygiene:BarSoap

        2013-06-03 * "Purchase"
            Assets:Bank:Checking                       -8,154 HUF
            Expenses:Hygiene:BarSoap                  (2+4)*4 PCS_DOVE_BAR_SOAP {1,699/4 HUF}
            Expenses:Hygiene:BarSoap             -(680+1,360) HUF
                discount-account: "Tesco:Clubcard"

        2013-07-03 * "Purchase"
            Assets:Bank:Checking                       -8,154 HUF
            Expenses:Hygiene:BarSoap                  (2+4)*4 PCS_DOVE_BAR_SOAP {1,699/4 HUF}
            Expenses:Hygiene:BarSoap             -(680+1,360) HUF
                discount-account: "Tesco:Clubcard"
        """
        config_str = ('{"manipulators": ['
                      '{'
                      f'  "type":"{manipulator_type}",'
                      '  "roundings":{'
                      '      "USD":2'
                      '    },'
                      '  "consolidate-price-account-postfix":"Price",'
                      '  "spread-base":"unit",'
                      '  "match-mode":"same-account",'
                      '  "metadata-name-spread-account-postfix":"discount-account"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 open Expenses:Hygiene:BarSoap:Price
        2010-08-31 open Expenses:Hygiene:BarSoap:Tesco:Clubcard

        2013-06-03 * "Purchase"
            Assets:Bank:Checking                             -8,154 HUF
            Expenses:Hygiene:BarSoap:Price                  (2+4)*4 PCS_DOVE_BAR_SOAP {1,699/4-(680+1,360)/((2+4)*4) HUF}
            Expenses:Hygiene:BarSoap:Price              (680+1,360) HUF
            Expenses:Hygiene:BarSoap:Tesco:Clubcard    -(680+1,360) HUF

        2013-07-03 * "Purchase"
            Assets:Bank:Checking                             -8,154 HUF
            Expenses:Hygiene:BarSoap:Price                  (2+4)*4 PCS_DOVE_BAR_SOAP {1,699/4-(680+1,360)/((2+4)*4) HUF}
            Expenses:Hygiene:BarSoap:Price              (680+1,360) HUF
            Expenses:Hygiene:BarSoap:Tesco:Clubcard    -(680+1,360) HUF
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_spread_posting_to_metadata_account_independency(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Hygiene:BarSoap
        2010-08-31 open Expenses:Hygiene:Cream

        2013-06-03 * "Purchase"
            Assets:Bank:Checking                       -8,154 HUF
            Expenses:Hygiene:Cream                        100 HUF
            Expenses:Hygiene:BarSoap                  (2+4)*4 PCS_DOVE_BAR_SOAP {1,699/4 HUF}
            Expenses:Hygiene:BarSoap             -(680+1,360) HUF
                discount-account: "Tesco:Clubcard"
        """
        config_str = ('{"manipulators": ['
                      '{'
                      f'  "type":"{manipulator_type}",'
                      '  "roundings":{'
                      '      "USD":2'
                      '    },'
                      '  "consolidate-price-account-postfix":"Price",'
                      '  "spread-base":"unit",'
                      '  "match-mode":"same-account",'
                      '  "metadata-name-spread-account-postfix":"discount-account"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 open Expenses:Hygiene:BarSoap:Price
        2010-08-31 open Expenses:Hygiene:BarSoap:Tesco:Clubcard
        2010-08-31 open Expenses:Hygiene:Cream

        2013-06-03 * "Purchase"
            Assets:Bank:Checking                             -8,154 HUF
            Expenses:Hygiene:Cream                              100 HUF
            Expenses:Hygiene:BarSoap:Price                  (2+4)*4 PCS_DOVE_BAR_SOAP {1,699/4-(680+1,360)/((2+4)*4) HUF}
            Expenses:Hygiene:BarSoap:Price              (680+1,360) HUF
            Expenses:Hygiene:BarSoap:Tesco:Clubcard    -(680+1,360) HUF
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_spread_posting_to_all_postings_negative(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Bread
        2010-08-31 open Expenses:Fruit
        2010-08-31 open Expenses:Milk

        2013-06-03 * "Purchase"
            Assets:Bank:Checking      -65 USD
            Expenses:Discount          -5 USD
                spread-source-id: "all"
                spread-base: "unit"
            Expenses:Bread             15 USD
            Expenses:Fruit             35 USD
            Expenses:Milk              20 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      f'  "type":"{manipulator_type}",'
                      '  "roundings":{'
                      '      "USD":2'
                      '    },'
                      '  "consolidate-price-account-postfix":"Price",'
                      '  "metadata-name-spread-base":"spread-base",'
                      '  "metadata-name-spread-source-id":"spread-source-id"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 open Expenses:Bread:Price
        2010-08-31 open Expenses:Bread:Discount
        2010-08-31 open Expenses:Fruit:Price
        2010-08-31 open Expenses:Fruit:Discount
        2010-08-31 open Expenses:Milk:Price
        2010-08-31 open Expenses:Milk:Discount

        2013-06-03 * "Purchase"
            Assets:Bank:Checking          -65 USD
            Expenses:Bread:Price           15 USD
            Expenses:Bread:Discount     -1.07 USD
            Expenses:Fruit:Price           35 USD
            Expenses:Fruit:Discount     -2.50 USD
            Expenses:Milk:Price            20 USD
            Expenses:Milk:Discount      -1.43 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_spread_posting_to_all_postings_positive(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Bread
        2010-08-31 open Expenses:Fruit
        2010-08-31 open Expenses:Milk

        2013-06-03 * "Purchase"
            Assets:Bank:Checking      -70 USD
            Expenses:Delivery           5 USD
                spread-source-id: "all"
                spread-base: "unit"
            Expenses:Bread             15 USD
            Expenses:Fruit             35 USD
            Expenses:Milk              20 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      f'  "type":"{manipulator_type}",'
                      '  "roundings":{'
                      '      "USD":2'
                      '    },'
                      '  "consolidate-price-account-postfix":"Price",'
                      '  "metadata-name-spread-base":"spread-base",'
                      '  "metadata-name-spread-source-id":"spread-source-id"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 open Expenses:Bread:Price
        2010-08-31 open Expenses:Bread:Delivery
        2010-08-31 open Expenses:Fruit:Price
        2010-08-31 open Expenses:Fruit:Delivery
        2010-08-31 open Expenses:Milk:Price
        2010-08-31 open Expenses:Milk:Delivery

        2013-06-03 * "Purchase"
            Assets:Bank:Checking          -70 USD
            Expenses:Bread:Price           15 USD
            Expenses:Bread:Delivery      1.07 USD
            Expenses:Fruit:Price           35 USD
            Expenses:Fruit:Delivery      2.50 USD
            Expenses:Milk:Price            20 USD
            Expenses:Milk:Delivery       1.43 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_spread_one_posting_to_specific_postings_negative(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Bread
        2010-08-31 open Expenses:Fruit
        2010-08-31 open Expenses:Milk

        2013-06-03 * "Purchase"
            Assets:Bank:Checking      -65 USD
            Expenses:Discount          -5 USD
                spread-source-id: "1"
                spread-base: "unit"
            Expenses:Bread             15 USD
                spread-target-id: "1"
            Expenses:Fruit             35 USD
            Expenses:Milk              20 USD
                spread-target-id: "1"
        """
        config_str = ('{"manipulators": ['
                      '{'
                      f'  "type":"{manipulator_type}",'
                      '  "roundings":{'
                      '      "USD":2'
                      '    },'
                      '  "consolidate-price-account-postfix":"Price",'
                      '  "metadata-name-spread-base":"spread-base",'
                      '  "metadata-name-spread-source-id":"spread-source-id",'
                      '  "metadata-name-spread-target-id":"spread-target-id"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 open Expenses:Bread:Price
        2010-08-31 open Expenses:Bread:Discount
        2010-08-31 open Expenses:Fruit
        2010-08-31 open Expenses:Milk:Price
        2010-08-31 open Expenses:Milk:Discount

        2013-06-03 * "Purchase"
            Assets:Bank:Checking          -65 USD
            Expenses:Bread:Price           15 USD
            Expenses:Bread:Discount     -2.14 USD
            Expenses:Milk:Price            20 USD
            Expenses:Milk:Discount      -2.86 USD
            Expenses:Fruit                 35 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_single_discount_split(self, entries, _, options_map):
        """
        2016-05-31 * ""
            Assets:Bank                1,170 HUF
            Expenses:Discount           -300 HUF
                spread-source-id: "1"
                spread-base: "unit"
            Expenses:Onion               150 HUF
            Expenses:Bread               620 HUF
                spread-target-id: "1"
            Expenses:Butter              400 HUF
                spread-target-id: "1"
            Expenses:Milk                300 HUF
                spread-target-id: "1"
        """
        config_str = ('{"manipulators": ['
                      '{'
                      f'  "type":"{manipulator_type}",'
                      '  "roundings":{'
                      '      "HUF":2'
                      '    },'
                      '  "consolidate-price-account-postfix":"Price",'
                      '  "metadata-name-spread-base":"spread-base",'
                      '  "metadata-name-spread-source-id":"spread-source-id",'
                      '  "metadata-name-spread-target-id":"spread-target-id"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2016-05-31 * ""
            discount-1:                     300 HUF
            Assets:Bank                   1,170 HUF
            Expenses:Onion                  150 HUF
            Expenses:Bread:Price            620 HUF
            Expenses:Bread:Discount     -140.91 HUF
            Expenses:Butter:Price           400 HUF
            Expenses:Butter:Discount     -90.91 HUF
            Expenses:Milk:Price             300 HUF
            Expenses:Milk:Discount       -68.18 HUF
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_multiple_discount_split(self, entries, _, options_map):
        """
        2016-05-31 * ""
            Assets:Bank                1,060 HUF
            Expenses:Discount           -110 HUF
                spread-source-id: "1"
                spread-base: "unit"
            Expenses:Discount           -300 HUF
                spread-source-id: "2"
                spread-base: "unit"
            Expenses:Onion               150 HUF
                spread-target-id: "1"
            Expenses:Bread               620 HUF
                spread-target-id: "1,2"
            Expenses:Butter              400 HUF
                spread-target-id: "2"
            Expenses:Milk                300 HUF
                spread-target-id: "2"
        """
        config_str = ('{"manipulators": ['
                      '{'
                      f'  "type":"{manipulator_type}",'
                      '  "roundings":{'
                      '      "HUF":2'
                      '    },'
                      '  "consolidate-price-account-postfix":"Price",'
                      '  "metadata-name-spread-base":"spread-base",'
                      '  "metadata-name-spread-source-id":"spread-source-id",'
                      '  "metadata-name-spread-target-id":"spread-target-id"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2016-05-31 * ""
            Assets:Bank                   1,060 HUF
            Expenses:Onion:Price            150 HUF
            Expenses:Onion:Discount      -21.43 HUF
            Expenses:Bread:Price            620 HUF
            Expenses:Bread:Discount     -229.48 HUF
            Expenses:Butter:Price           400 HUF
            Expenses:Butter:Discount     -90.91 HUF
            Expenses:Milk:Price             300 HUF
            Expenses:Milk:Discount       -68.18 HUF
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_single_discount_split_adapt_accounts(self, entries, _, options_map):
        """
        2010-08-31 open Expenses:Bread
        2010-08-31 open Expenses:Butter

        2016-05-20 * ""
            Assets:Bank                  200 HUF
            Expenses:Bread               200 HUF

        2016-05-25 * ""
            Assets:Bank                  380 HUF
            Expenses:Discount            -20 HUF
                spread-source-id: "1"
                spread-base: "unit"
            Expenses:Discount           -100 HUF
                spread-source-id: "2"
                spread-base: "unit"
            Expenses:Onion               100 HUF
                spread-target-id: "1"
            Expenses:Bread               200 HUF
                spread-target-id: "2"
            Expenses:Butter              200 HUF
                spread-target-id: "2"

        2016-05-31 * ""
            Expenses:Discount            -20 HUF
                spread-source-id: "1"
                spread-base: "unit"
            Expenses:Discount           -100 HUF
                spread-source-id: "2"
                spread-base: "unit"
            Assets:Bank                  380 HUF
            Expenses:Onion               100 HUF
                spread-target-id: "1"
            Expenses:Bread               200 HUF
                spread-target-id: "2"
            Expenses:Butter              200 HUF
                spread-target-id: "2"
        """
        config_str = ('{"manipulators": ['
                      '{'
                      f'  "type":"{manipulator_type}",'
                      '  "roundings":{'
                      '      "HUF":0'
                      '    },'
                      '  "consolidate-price-account-postfix":"Price",'
                      '  "metadata-name-spread-base":"spread-base",'
                      '  "metadata-name-spread-source-id":"spread-source-id",'
                      '  "metadata-name-spread-target-id":"spread-target-id"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2010-08-31 open Expenses:Bread:Price
        2010-08-31 open Expenses:Bread:Discount
        2010-08-31 open Expenses:Butter:Price
        2010-08-31 open Expenses:Butter:Discount

        2016-05-20 * ""
            Assets:Bank                     200 HUF
            Expenses:Bread:Price            200 HUF

        2016-05-25 * ""
            discount-1:                      20 HUF
            discount-2:                     100 HUF
            Assets:Bank                     380 HUF
            Expenses:Onion:Price            100 HUF
            Expenses:Onion:Discount         -20 HUF
            Expenses:Bread:Price            200 HUF
            Expenses:Bread:Discount         -50 HUF
            Expenses:Butter:Price           200 HUF
            Expenses:Butter:Discount        -50 HUF

        2016-05-31 * ""
            discount-1:                      20 HUF
            discount-2:                     100 HUF
            Assets:Bank                     380 HUF
            Expenses:Onion:Price            100 HUF
            Expenses:Onion:Discount         -20 HUF
            Expenses:Bread:Price            200 HUF
            Expenses:Bread:Discount         -50 HUF
            Expenses:Butter:Price           200 HUF
            Expenses:Butter:Discount        -50 HUF
        """,
            new_entries,
        )


if __name__ == '__main__':
    unittest.main()
