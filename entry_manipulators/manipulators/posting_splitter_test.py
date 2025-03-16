import decimal
import unittest

from beancount import loader, Amount
from beancount.parser import cmptest

from entry_manipulators.entry_manipulator_orchestrator import entry_manipulator


class TestPostingSplitter(cmptest.TestCase):

    @loader.load_doc(expect_errors=True)
    def test_no_split(self, entries, _, options_map):
        """
        2016-05-31 * "Exams"
            Assets:Bank                 -800 HUF
            Expenses:Exam                800 HUF
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-splitter",'
                      '  "metadata-name-type":"split-mode"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulator(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2016-05-31 * "Exams"
            Assets:Bank                 -800 HUF
            Expenses:Exam                800 HUF
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_equal_split(self, entries, _, options_map):
        """
        2016-05-31 * "Exams"
            Assets:Bank                 -800 HUF
                split-mode: "equal"
            Expenses:Exam                  0 HUF
            Expenses:Exam                  0 HUF
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-splitter",'
                      '  "metadata-name-type":"split-mode"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulator(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2016-05-31 * "Exams"
            Assets:Bank                 -800 HUF
            Expenses:Exam                400 HUF
            Expenses:Exam                400 HUF
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_equal_split_check_metadata(self, entries, _, options_map):
        """
        2016-05-31 * "Exams"
            Assets:Bank                 -800 HUF
                split-mode: "equal"
                narration: "exams"
            Expenses:Exam                  0 HUF
                narration: "Exam A"
            Expenses:Exam                  0 HUF
                narration: "Exam B"
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-splitter",'
                      '  "metadata-name-type":"split-mode"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulator(entries, options_map, config_str)

        for entry in new_entries:
            for index, posting in enumerate(entry.postings):
                self.assertIsNotNone(posting.meta, posting)
                if index == 0:
                    self.assertEqual(posting.meta.get("split-mode"), None)
                    self.assertEqual(posting.meta.get("narration"), "exams")
                elif index == 1:
                    self.assertEqual(posting.meta.get("narration"), "Exam A")
                elif index == 2:
                    self.assertEqual(posting.meta.get("narration"), "Exam B")

    @loader.load_doc(expect_errors=True)
    def test_equal_split_rounding(self, entries, _, options_map):
        """
        2016-05-31 * "Exams"
            Assets:Bank                 -800 HUF
                split-mode: "equal"
            Expenses:Exam                  0 HUF
            Expenses:Exam                  0 HUF
            Expenses:Exam                  0 HUF
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-splitter",'
                      '  "roundings":{'
                      '      "HUF":2'
                      '    },'
                      '  "metadata-name-type":"split-mode"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulator(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2016-05-31 * "Exams"
            Assets:Bank                 -800 HUF
            Expenses:Exam             266.67 HUF
            Expenses:Exam             266.67 HUF
            Expenses:Exam             266.67 HUF
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_equal_split_with_non_zero_posting(self, entries, _, options_map):
        """
        2016-05-31 * "Exams"
            Assets:Bank                 -500 HUF
                split-mode: "equal"
            Expenses:Exam                  0 HUF
            Expenses:Exam                100 HUF
            Expenses:Exam                  0 HUF
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-splitter",'
                      '  "metadata-name-type":"split-mode"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulator(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2016-05-31 * "Exams"
            Assets:Bank                 -500 HUF
            Expenses:Exam                200 HUF
            Expenses:Exam                100 HUF
            Expenses:Exam                200 HUF
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_equal_split_with_zero_posting_to_skip(self, entries, _, options_map):
        """
        2016-05-31 * "Exams"
            Assets:Bank                 -500 HUF
                split-mode: "equal"
            Expenses:Exam                  0 HUF
            Expenses:Exam                  0 HUF
                skip-split: ""
            Expenses:Exam                  0 HUF
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-splitter",'
                      '  "metadata-name-type":"split-mode",'
                      '  "metadata-name-skip-split":"skip-split"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulator(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2016-05-31 * "Exams"
            Assets:Bank                 -500 HUF
            Expenses:Exam                250 HUF
            Expenses:Exam                  0 HUF
            Expenses:Exam                250 HUF
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_proportional_split(self, entries, _, options_map):
        """
        2016-05-31 * "Exams"
            Assets:Bank                     -4 USD
                split-mode: "proportional"
            Expenses:Exam                    0 USD
                msrp:                       20 USD
            Expenses:Exam                    0 USD
                msrp:                       60 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-splitter",'
                      '  "metadata-name-type":"split-mode",'
                      '  "metadata-name-split-ratio":"msrp"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulator(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2016-05-31 * "Exams"
            Assets:Bank                 -4 USD
            Expenses:Exam             1.00 USD
                msrp:                   20 USD
            Expenses:Exam             3.00 USD
                msrp:                   60 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_proportional_split_check_metadata(self, entries, _, options_map):
        """
        2016-05-31 * "Exams"
            Assets:Bank                     -4 USD
                split-mode: "proportional"
                narration: "exams"
            Expenses:Exam                    0 USD
                msrp:                       20 USD
                narration: "Exam A"
            Expenses:Exam                    0 USD
                msrp:                       60 USD
                narration: "Exam B"
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-splitter",'
                      '  "metadata-name-type":"split-mode",'
                      '  "metadata-name-split-ratio":"msrp"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulator(entries, options_map, config_str)

        for entry in new_entries:
            for index, posting in enumerate(entry.postings):
                self.assertIsNotNone(posting.meta, posting)
                if index == 0:
                    self.assertEqual(posting.meta.get("split-mode"), None)
                    self.assertEqual(posting.meta.get("narration"), "exams")
                elif index == 1:
                    self.assertEqual(posting.meta.get("narration"), "Exam A")
                elif index == 2:
                    self.assertEqual(posting.meta.get("narration"), "Exam B")

    @loader.load_doc(expect_errors=True)
    def test_proportional_split_rounding(self, entries, _, options_map):
        """
        2016-05-31 * "Exams"
            Assets:Bank                    -19.99 USD
                split-mode: "proportional"
            Expenses:Exam                       0 USD
                msrp:                       20.99 USD
            Expenses:Exam                       0 USD
                msrp:                       60.99 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-splitter",'
                      '  "roundings":{'
                      '      "USD":2'
                      '    },'
                      '  "metadata-name-type":"split-mode",'
                      '  "metadata-name-split-ratio":"msrp"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulator(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2016-05-31 * "Exams"
            Assets:Bank                    -19.99 USD
            Expenses:Exam                    5.12 USD
            Expenses:Exam                   14.87 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_proportional_split_ignore_posts_without_metadata(self, entries, _, options_map):
        """
        2016-05-31 * "Exams"
            Assets:Bank                     -4 USD
                split-mode: "proportional"
            Expenses:Exam                    0 USD
                msrp:                       20 USD
            Expenses:Exam                    0 USD
            Expenses:Exam                    0 USD
                msrp:                       60 USD
            Expenses:Exam                    0 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-splitter",'
                      '  "metadata-name-type":"split-mode",'
                      '  "metadata-name-split-ratio":"msrp"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulator(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2016-05-31 * "Exams"
            Assets:Bank                 -4 USD
            Expenses:Exam             1.00 USD
                msrp:                   20 USD
            Expenses:Exam                    0 USD
            Expenses:Exam             3.00 USD
                msrp:                   60 USD
            Expenses:Exam                    0 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_proportional_with_cost_split(self, entries, _, options_map):
        """
        2016-05-31 * "Game bundle"
            Assets:Bank                 -800 HUF
                split-mode: "proportional"
                price:                  4.00 USD
                exchange-rate:           200 HUF
            Expenses:Games                 0 USD
                narration: "Game A"
                msrp:                  10.00 USD
            Expenses:Games                 0 USD
                narration: "Game B"
                msrp:                  30.00 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-splitter",'
                      '  "metadata-name-type":"split-mode",'
                      '  "metadata-name-unit":"price",'
                      '  "metadata-name-exchange-rate":"exchange-rate",'
                      '  "metadata-name-split-ratio":"msrp"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulator(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2016-05-31 * "Game bundle"
            Assets:Bank                 -800 HUF
                price:                  4.00 USD
            Expenses:Games            1.0000 USD {200 HUF}
                narration: "Game A"
                msrp:                  10.00 USD
            Expenses:Games            3.0000 USD {200 HUF}
                narration: "Game B"
                msrp:                  30.00 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_proportional_with_cost_split_check_metadata(self, entries, _, options_map):
        """
        2016-05-31 * "Game bundle"
            Assets:Bank                 -800 HUF
                split-mode: "proportional"
                price:                  4.00 USD
                exchange-rate:           200 HUF
            Expenses:Games                 0 USD
                narration: "Game A"
                msrp:                  10.00 USD
            Expenses:Games                 0 USD
                narration: "Game B"
                msrp:                  30.00 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-splitter",'
                      '  "metadata-name-type":"split-mode",'
                      '  "metadata-name-unit":"price",'
                      '  "metadata-name-exchange-rate":"exchange-rate",'
                      '  "metadata-name-split-ratio":"msrp"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulator(entries, options_map, config_str)

        for entry in new_entries:
            for index, posting in enumerate(entry.postings):
                self.assertIsNotNone(posting.meta, posting)
                if index == 0:
                    self.assertEqual(posting.meta.get("split-mode"), None)
                    self.assertEqual(posting.meta.get("exchange-rate"), None)
                    self.assertEqual(posting.meta.get("price"), Amount(decimal.Decimal(4), "USD"))
                elif index == 1:
                    self.assertEqual(posting.meta.get("narration"), "Game A")
                    self.assertEqual(posting.meta.get("msrp"), Amount(decimal.Decimal(10), "USD"))
                elif index == 2:
                    self.assertEqual(posting.meta.get("narration"), "Game B")
                    self.assertEqual(posting.meta.get("msrp"), Amount(decimal.Decimal(30), "USD"))

    @loader.load_doc(expect_errors=True)
    def test_proportional_with_cost_split_rounding(self, entries, _, options_map):
        """
        2016-05-31 * "Game bundle"
            Assets:Bank                 -961 HUF
                split-mode: "proportional"
                price:                  4.34 USD
                exchange-rate:         221.5 HUF
            Expenses:Games                 0 USD
                narration: "Game A"
                msrp:                  19.99 USD
            Expenses:Games                 0 USD
                narration: "Game B"
                msrp:                  39.99 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-splitter",'
                      '  "roundings":{'
                      '      "USD":4'
                      '    },'
                      '  "metadata-name-type":"split-mode",'
                      '  "metadata-name-unit":"price",'
                      '  "metadata-name-exchange-rate":"exchange-rate",'
                      '  "metadata-name-split-ratio":"msrp"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulator(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2016-05-31 * "Game bundle"
            Assets:Bank                 -961 HUF
                price:                  4.00 USD
            Expenses:Games            1.4464 USD {221.5 HUF}
                narration: "Game A"
                msrp:                  19.99 USD
            Expenses:Games            2.8936 USD {221.5 HUF}
                narration: "Game B"
                msrp:                  39.99 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_single_discount_split(self, entries, _, options_map):
        """
        2016-05-31 * ""
            split-mode: "discount"
            discount-1:                  300 HUF
            Assets:Bank                1,170 HUF
            Expenses:Onion               150 HUF
            Expenses:Bread               620 HUF
                discount-ids: "1"
            Expenses:Butter              400 HUF
                discount-ids: "1"
            Expenses:Milk                300 HUF
                discount-ids: "1"
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-splitter",'
                      '  "metadata-name-type":"split-mode",'
                      '  "roundings":{'
                      '      "HUF":2'
                      '    },'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulator(entries, options_map, config_str)

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
            split-mode: "discount"
            discount-1:                  110 HUF
            discount-2:                  300 HUF
            Assets:Bank                1,060 HUF
            Expenses:Onion               150 HUF
                discount-ids: "1"
            Expenses:Bread               620 HUF
                discount-ids: "1,2"
            Expenses:Butter              400 HUF
                discount-ids: "2"
            Expenses:Milk                300 HUF
                discount-ids: "2"
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-splitter",'
                      '  "metadata-name-type":"split-mode",'
                      '  "roundings":{'
                      '      "HUF":2'
                      '    },'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulator(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2016-05-31 * ""
            discount-1:                     110 HUF
            discount-2:                     300 HUF
            Assets:Bank                   1,060 HUF
            Expenses:Onion:Price            150 HUF
            Expenses:Onion:Discount      -21.43 HUF
            Expenses:Bread:Price            620 HUF
            Expenses:Bread:Discount      -88.57 HUF
            Expenses:Bread:Discount     -140.91 HUF
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
            split-mode: "discount"
            discount-1:                   20 HUF
            discount-2:                  100 HUF
            Assets:Bank                  380 HUF
            Expenses:Onion               100 HUF
                discount-ids: "1"
            Expenses:Bread               200 HUF
                discount-ids: "2"
            Expenses:Butter              200 HUF
                discount-ids: "2"

        2016-05-31 * ""
            split-mode: "discount"
            discount-1:                   20 HUF
            discount-2:                  100 HUF
            Assets:Bank                  380 HUF
            Expenses:Onion               100 HUF
                discount-ids: "1"
            Expenses:Bread               200 HUF
                discount-ids: "2"
            Expenses:Butter              200 HUF
                discount-ids: "2"
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"posting-splitter",'
                      '  "metadata-name-type":"split-mode",'
                      '  "roundings":{'
                      '      "HUF":0'
                      '  }'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulator(entries, options_map, config_str)

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
