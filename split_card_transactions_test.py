import unittest

from beancount.parser import cmptest
from beancount import loader
from split_card_transactions import split_card_transactions


class TestSplitCardTransaction(cmptest.TestCase):
    @loader.load_doc(expect_errors=True)
    def test_split_card_transactions(self, entries, _, options_map):
        """
        2013-05-31 * "Paid by card"
            Assets:Bank:Checking      -100 USD
                booking-transfer-account: Assets:Bank:DebitCard
                booking-date: 2013-06-03
            Assets:Cash                100 USD
        """
        new_entries, _ = split_card_transactions(entries, options_map)

        self.assertEqualEntries(
            """
        2013-05-31 * "Paid by card"
            Assets:Bank:DebitCard     -100 USD
            Assets:Cash                100 USD

        2013-06-03 * "Card transaction booking"
            Assets:Bank:Checking      -100 USD
            Assets:Bank:DebitCard      100 USD
        """,
            new_entries,
        )


if __name__ == "__main__":
    unittest.main()
