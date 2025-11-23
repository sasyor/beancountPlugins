from beancount import loader
from beancount.parser import cmptest

from utility_bill.utility_bill import utility_bill


class TestUtilityBill(cmptest.TestCase):

    @loader.load_doc(expect_errors=True)
    def test_single_1(self, entries, _, options_map):
        """
        2022-02-26 * "V-V" "Részszámla 1"
            utility-type: "electricity"
            period-start: 2022-01-04
            period-end:   2022-02-22
            usage-kwh:    213
            estimated:    TRUE
            Assets:Bank                      -7,865 HUF
            Expenses:Utilities:Electricity    7,865 HUF
        """
        config_str = ('{"utilities": ['
                      '{'
                      '  "type":"electricity",'
                      '  "shared-account":"Expenses:Utilities:Electricity",'
                      '  "transfer-account":"Assets:Utilities:Electricity"'
                      '}'
                      ']}')
        new_entries, _ = utility_bill(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2022-02-26 * "V-V" "Részszámla 1"
            Assets:Bank                      -7,865 HUF
            Assets:Utilities:Electricity      7,865 HUF

        2022-01-31 * "V-V" "Részszámla 1"
            Assets:Utilities:Electricity     -4,334 HUF
            Expenses:Utilities:Electricity    4,334 HUF

        2022-02-22 * "V-V" "Részszámla 1"
            Assets:Utilities:Electricity     -3,531 HUF
            Expenses:Utilities:Electricity    3,531 HUF
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_single_2(self, entries, _, options_map):
        """
        2022-04-25 * "V-V" "Részszámla 2"
            utility-type: "electricity"
            period-start: 2022-02-23
            period-end:   2022-04-25
            usage-kwh:    252
            estimated:    TRUE
            Assets:Bank                      -9,431 HUF
            Expenses:Utilities:Electricity    9,431 HUF
        """
        config_str = ('{"utilities": ['
                      '{'
                      '  "type":"electricity",'
                      '  "shared-account":"Expenses:Utilities:Electricity",'
                      '  "transfer-account":"Assets:Utilities:Electricity"'
                      '}'
                      ']}')
        new_entries, _ = utility_bill(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2022-04-25 * "V-V" "Részszámla 2"
            Assets:Bank                      -9,431 HUF
            Assets:Utilities:Electricity      9,431 HUF

        2022-02-28 * "V-V" "Részszámla 2"
            Assets:Utilities:Electricity       -773 HUF
            Expenses:Utilities:Electricity      773 HUF

        2022-03-31 * "V-V" "Részszámla 2"
            Assets:Utilities:Electricity     -4,793 HUF
            Expenses:Utilities:Electricity    4,793 HUF

        2022-04-25 * "V-V" "Részszámla 2"
            Assets:Utilities:Electricity     -3,865 HUF
            Expenses:Utilities:Electricity    3,865 HUF
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_multiple_1(self, entries, _, options_map):
        """
        2022-02-26 * "V-V" "Részszámla 1"
            utility-type: "electricity"
            period-start: 2022-01-04
            period-end:   2022-02-22
            usage-kwh:    213
            estimated:    TRUE
            Assets:Bank                      -7,865 HUF
            Expenses:Utilities:Electricity    7,865 HUF

        2022-04-25 * "V-V" "Részszámla 2"
            utility-type: "electricity"
            period-start: 2022-02-23
            period-end:   2022-04-25
            usage-kwh:    252
            estimated:    TRUE
            Assets:Bank                      -9,431 HUF
            Expenses:Utilities:Electricity    9,431 HUF
        """
        config_str = ('{"utilities": ['
                      '{'
                      '  "type":"electricity",'
                      '  "shared-account":"Expenses:Utilities:Electricity",'
                      '  "transfer-account":"Assets:Utilities:Electricity"'
                      '}'
                      ']}')
        new_entries, _ = utility_bill(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2022-02-26 * "V-V" "Részszámla 1"
            Assets:Bank                      -7,865 HUF
            Assets:Utilities:Electricity      7,865 HUF

        2022-01-31 * "V-V" "Részszámla 1"
            Assets:Utilities:Electricity     -4,334 HUF
            Expenses:Utilities:Electricity    4,334 HUF

        2022-02-22 * "V-V" "Részszámla 1"
            Assets:Utilities:Electricity     -3,531 HUF
            Expenses:Utilities:Electricity    3,531 HUF

        2022-04-25 * "V-V" "Részszámla 2"
            Assets:Bank                      -9,431 HUF
            Assets:Utilities:Electricity      9,431 HUF

        2022-02-28 * "V-V" "Részszámla 2"
            Assets:Utilities:Electricity       -773 HUF
            Expenses:Utilities:Electricity      773 HUF

        2022-03-31 * "V-V" "Részszámla 2"
            Assets:Utilities:Electricity     -4,793 HUF
            Expenses:Utilities:Electricity    4,793 HUF

        2022-04-25 * "V-V" "Részszámla 2"
            Assets:Utilities:Electricity     -3,865 HUF
            Expenses:Utilities:Electricity    3,865 HUF
        """,
            new_entries,
        )
