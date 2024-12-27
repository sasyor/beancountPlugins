import unittest

from beancount.parser import cmptest
from beancount import loader
from split_card_transactions import split_card_transactions


class TestSplitCardTransaction(cmptest.TestCase):
    @loader.load_doc(expect_errors=True)
    def test_split_card_transactions_default_options(self, entries, _, options_map):
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

    @loader.load_doc(expect_errors=True)
    def test_split_card_transactions_custom_booking_posting_narration_options(self, entries, _, options_map):
        """
        2013-05-31 * "Paid by card"
            Assets:Bank:Checking      -100 USD
                booking-transfer-account: Assets:Bank:DebitCard
                booking-date: 2013-06-03
            Assets:Cash                100 USD
        """
        new_entries, _ = split_card_transactions(entries, options_map, '{"booking_posting_narration":"Test narration"}')

        self.assertEqualEntries(
            """
        2013-05-31 * "Paid by card"
            Assets:Bank:DebitCard     -100 USD
            Assets:Cash                100 USD

        2013-06-03 * "Test narration"
            Assets:Bank:Checking      -100 USD
            Assets:Bank:DebitCard      100 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_split_card_transactions_custom_booking_date_options(self, entries, _, options_map):
        """
        2013-05-31 * "Paid by card"
            Assets:Bank:Checking      -100 USD
                booking-transfer-account: Assets:Bank:DebitCard
                custom-metadata: 2013-06-03
            Assets:Cash                100 USD
        """
        new_entries, _ = split_card_transactions(entries, options_map, '{"booking_date":"custom-metadata"}')

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

    @loader.load_doc(expect_errors=True)
    def test_split_card_transactions_custom_booking_transfer_account_options(self, entries, _, options_map):
        """
        2013-05-31 * "Paid by card"
            Assets:Bank:Checking      -100 USD
                custom-metadata: Assets:Bank:DebitCard
                booking-date: 2013-06-03
            Assets:Cash                100 USD
        """
        new_entries, _ = split_card_transactions(entries, options_map, '{"booking_transfer_account":"custom-metadata"}')

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

    @loader.load_doc(expect_errors=True)
    def test_split_card_transactions_account_based_splitters_options(self, entries, _, options_map):
        """
        2013-05-31 * "Paid by card"
            Assets:Bank:Checking      -100 USD
                booking-date: 2013-06-03
            Assets:Cash                100 USD
        """
        new_entries, _ = split_card_transactions(entries, options_map, '{"account_based_splitters":[{'
                                                                       '"account":"Assets:Bank:Checking",'
                                                                       '"transfer_account":"Assets:Bank:DebitCard"}]}')

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
