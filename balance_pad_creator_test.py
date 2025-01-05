import datetime
import unittest

from beancount import loader
from beancount.core import data
from beancount.core.amount import A
from beancount.parser import cmptest

from balance_pad_creator import balance_pad_creator


class TestBalancePadCreator(cmptest.TestCase):

    @loader.load_doc(expect_errors=True)
    def test_balance_creation(self, entries, _, options_map):
        """
        2013-05-31 * "Entry"
            Assets:Bank:Checking      -100 USD
            Assets:Telephone           100 USD
                balance:               100 USD
                balance-time: "14:47"
        """
        config_str = ('{'
                      '"account":"Assets:Telephone",'
                      '"metadata-name-balance-unit":"balance",'
                      '"metadata-name-balance-time":"balance-time"'
                      '}')
        new_entries, _ = balance_pad_creator(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "Entry"
            Assets:Bank:Checking      -100 USD
            Assets:Telephone           100 USD

        2013-06-01 balance Assets:Telephone  100 USD
           balance-time: "14:47"
           type: "upload"
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_balance_creation_metadata_balance_time(self, entries, _, options_map):
        """
        2013-05-31 * "Entry"
            Assets:Bank:Checking      -100 USD
            Assets:Telephone           100 USD
                balance:               100 USD
                balance-time: "14:47"
        """
        config_str = ('{'
                      '"account":"Assets:Telephone",'
                      '"metadata-name-balance-unit":"balance",'
                      '"metadata-name-balance-time":"balance-time"'
                      '}')
        new_entries, _ = balance_pad_creator(entries, options_map, config_str)

        for entry in new_entries:
            if not isinstance(entry, data.Balance):
                continue
            self.assertEqual(entry.meta.get("balance-time"), "14:47")

    @loader.load_doc(expect_errors=True)
    def test_balance_consolidation_no_creation(self, entries, _, options_map):
        """
        2013-05-31 * "Entry"
            Assets:Bank:Checking      -100 USD
            Assets:Telephone           100 USD
                balance:               100 USD
                balance-time: "14:47"
        """
        entries.append(data.Balance(
            data.new_metadata(".", 1001, {"balance-time": "14:48"}), datetime.date(2013, 6, 1), "Assets:Telephone",
            A('100 USD"'), None, None
        ))
        config_str = ('{'
                      '"account":"Assets:Telephone",'
                      '"metadata-name-balance-unit":"balance",'
                      '"metadata-name-balance-time":"balance-time"'
                      '}')
        new_entries, _ = balance_pad_creator(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "Entry"
            Assets:Bank:Checking      -100 USD
            Assets:Telephone           100 USD

        2013-06-01 balance Assets:Telephone  100 USD
           balance-time: "14:48"
        """,
            new_entries,
        )
        actual_entries = list(filter(lambda entry: isinstance(entry, data.Balance), new_entries))
        self.assertEqual(len(actual_entries), 1, actual_entries)
        self.assertEqual(actual_entries[0].meta.get("balance-time"), "14:48")

    @loader.load_doc(expect_errors=True)
    def test_balance_consolidation_with_creation(self, entries, _, options_map):
        """
        2013-05-31 * "Entry"
            Assets:Bank:Checking      -100 USD
            Assets:Telephone           100 USD
                balance:               100 USD
                balance-time: "14:48"
        """
        entries.append(data.Balance(
            data.new_metadata(".", 1001, {"balance-time": "14:47"}), datetime.date(2013, 6, 1), "Assets:Telephone",
            A('100 USD"'), None, None
        ))
        config_str = ('{'
                      '"account":"Assets:Telephone",'
                      '"metadata-name-balance-unit":"balance",'
                      '"metadata-name-balance-time":"balance-time"'
                      '}')
        new_entries, _ = balance_pad_creator(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "Entry"
            Assets:Bank:Checking      -100 USD
            Assets:Telephone           100 USD

        2013-06-01 balance Assets:Telephone  100 USD
           balance-time: "14:48"
        """,
            new_entries,
        )
        actual_entries = list(filter(lambda entry: isinstance(entry, data.Balance), new_entries))
        self.assertEqual(len(actual_entries), 1, actual_entries)
        self.assertEqual(actual_entries[0].meta.get("balance-time"), "14:48")

    @loader.load_doc(expect_errors=True)
    def test_pad_creation(self, entries, _, options_map):
        """
        2013-05-31 * "Entry"
            Assets:Bank:Checking      -100 USD
            Assets:Telephone           100 USD
        """
        date = datetime.date(2013, 6, 1)
        account = 'Assets:Telephone'
        entries.append(data.Balance(
            data.new_metadata(".", 1001, {"balance-time": "14:47"}), date, account,
            A('80 USD"'), None, None
        ))
        config_str = ('{'
                      '"account":"Assets:Telephone",'
                      '"pad-account":"Expenses:Telephone:CallsAndMessages",'
                      '"metadata-name-balance-unit":"balance",'
                      '"metadata-name-balance-time":"balance-time"'
                      '}')
        new_entries, _ = balance_pad_creator(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "Entry"
            Assets:Bank:Checking      -100 USD
            Assets:Telephone           100 USD

        2013-05-31 pad Assets:Telephone Expenses:Telephone:CallsAndMessages

        2013-06-01 balance Assets:Telephone  80 USD
           balance-time: "14:47"
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_pad_creation_and_no_creation(self, entries, _, options_map):
        """
        2013-05-31 * "Entry"
            Assets:Bank:Checking      -100 USD
            Assets:Telephone           100 USD

        2013-06-22 * "Entry"
            Assets:Bank:Checking      -100 USD
            Assets:Telephone           100 USD
        """
        date = datetime.date(2013, 6, 1)
        account = 'Assets:Telephone'
        entries.append(data.Balance(
            data.new_metadata(".", 1001, {"balance-time": "14:47"}), date, account,
            A('80 USD"'), None, None
        ))
        date = datetime.date(2013, 6, 28)
        entries.append(data.Balance(
            data.new_metadata(".", 1001, {"balance-time": "14:47"}), date, account,
            A('180 USD"'), None, None
        ))
        config_str = ('{'
                      '"account":"Assets:Telephone",'
                      '"pad-account":"Expenses:Telephone:CallsAndMessages",'
                      '"metadata-name-balance-unit":"balance",'
                      '"metadata-name-balance-time":"balance-time"'
                      '}')
        new_entries, _ = balance_pad_creator(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "Entry"
            Assets:Bank:Checking      -100 USD
            Assets:Telephone           100 USD

        2013-06-22 * "Entry"
            Assets:Bank:Checking      -100 USD
            Assets:Telephone           100 USD

        2013-06-01 balance Assets:Telephone  80 USD
           balance-time: "14:47"
           
        2013-06-28 balance Assets:Telephone  180 USD
           balance-time: "14:47"

        2013-05-31 pad Assets:Telephone Expenses:Telephone:CallsAndMessages
        """,
            new_entries,
        )


if __name__ == '__main__':
    unittest.main()
