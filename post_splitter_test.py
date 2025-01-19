import decimal
import unittest

from beancount import loader, Amount
from beancount.parser import cmptest

from post_splitter import post_splitter


class TestPostSplitter(cmptest.TestCase):

    @loader.load_doc(expect_errors=True)
    def test_equal_split(self, entries, _, options_map):
        """
        2016-05-31 * "Exams"
            Assets:Bank                 -800 HUF
                split-mode: "equal"
            Expenses:Exam                  0 HUF
            Expenses:Exam                  0 HUF
        """
        config_str = ('{'
                      '"metadata-name-type":"split-mode"'
                      '}')
        new_entries, _ = post_splitter(entries, options_map, config_str)

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
        config_str = ('{'
                      '"metadata-name-type":"split-mode"'
                      '}')
        new_entries, _ = post_splitter(entries, options_map, config_str)

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
        config_str = ('{'
                      '"roundings":{'
                      '    "HUF":2'
                      '  },'
                      '"metadata-name-type":"split-mode"'
                      '}')
        new_entries, _ = post_splitter(entries, options_map, config_str)

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
    def test_cost_split(self, entries, _, options_map):
        """
        2016-05-31 * "Game bundle"
            Assets:Bank                 -800 HUF
                split-mode: "cost"
                price:                  4.00 USD
                exchange-rate:           200 HUF
            Expenses:Games                 0 USD
                narration: "Game A"
                msrp:                  10.00 USD
            Expenses:Games                 0 USD
                narration: "Game B"
                msrp:                  30.00 USD
        """
        config_str = ('{'
                      '"metadata-name-type":"split-mode",'
                      '"metadata-name-unit":"price",'
                      '"metadata-name-exchange-rate":"exchange-rate",'
                      '"metadata-name-split-ratio":"msrp"'
                      '}')
        new_entries, _ = post_splitter(entries, options_map, config_str)

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
    def test_cost_split_check_metadata(self, entries, _, options_map):
        """
        2016-05-31 * "Game bundle"
            Assets:Bank                 -800 HUF
                split-mode: "cost"
                price:                  4.00 USD
                exchange-rate:           200 HUF
            Expenses:Games                 0 USD
                narration: "Game A"
                msrp:                  10.00 USD
            Expenses:Games                 0 USD
                narration: "Game B"
                msrp:                  30.00 USD
        """
        config_str = ('{'
                      '"metadata-name-type":"split-mode",'
                      '"metadata-name-unit":"price",'
                      '"metadata-name-exchange-rate":"exchange-rate",'
                      '"metadata-name-split-ratio":"msrp"'
                      '}')
        new_entries, _ = post_splitter(entries, options_map, config_str)

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
    def test_cost_split_rounding(self, entries, _, options_map):
        """
        2016-05-31 * "Game bundle"
            Assets:Bank                 -961 HUF
                split-mode: "cost"
                price:                  4.34 USD
                exchange-rate:         221.5 HUF
            Expenses:Games                 0 USD
                narration: "Game A"
                msrp:                  19.99 USD
            Expenses:Games                 0 USD
                narration: "Game B"
                msrp:                  39.99 USD
        """
        config_str = ('{'
                      '"roundings":{'
                      '    "USD":4'
                      '  },'
                      '"metadata-name-type":"split-mode",'
                      '"metadata-name-unit":"price",'
                      '"metadata-name-exchange-rate":"exchange-rate",'
                      '"metadata-name-split-ratio":"msrp"'
                      '}')
        new_entries, _ = post_splitter(entries, options_map, config_str)

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


if __name__ == '__main__':
    unittest.main()
