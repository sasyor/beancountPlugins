import unittest

from beancount.core import data
from beancount.parser import cmptest
from beancount import loader

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
                      '"metadata-name-balance-unit":"balance",'
                      '"metadata-name-balance-time":"balance-time"'
                      '}')
        new_entries, _ = balance_pad_creator(entries, options_map, config_str)

        for entry in new_entries:
            if not isinstance(entry, data.Balance):
                continue
            self.assertEqual(entry.meta.get("balance-time"), "14:47")


if __name__ == '__main__':
    unittest.main()
