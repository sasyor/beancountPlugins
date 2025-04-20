import unittest

from beancount import loader
from beancount.parser import cmptest

from entry_manipulators.entry_manipulators import entry_manipulators


class TestTransactionSplitter(cmptest.TestCase):

    @loader.load_doc(expect_errors=True)
    def test_metadata_retention(self, entries, _, options_map):
        """
        2013-05-31 * "Paid by card"
            random-1: "text-1"
            Assets:Bank:Checking      -100 USD
                booking-date: 2013-06-03
                random-2: "text-2"
            Assets:Cash                100 USD
                random-3: "text-3"
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"transaction-splitter",'
                      '  "metadata-name-date":"booking-date",'
                      '  "transfer-account":"Liabilities:Bank:DebitCard",'
                      '  "dated-posting-move-mode":"move"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        for entry in new_entries:
            self.assertEqual(entry.meta.get("random-1"), "text-1", entry)
            for posting in entry.postings:
                if posting.account == "Assets:Bank:Checking":
                    self.assertEqual("text-2", posting.meta.get("random-2"), posting)
                    self.assertIsNone(posting.meta.get("random-3"), posting)
                if posting.account == "Assets:Cash":
                    self.assertIsNone(posting.meta.get("random-2"), posting)
                    self.assertEqual("text-3", posting.meta.get("random-3"), posting)

    @loader.load_doc(expect_errors=True)
    def test_metadata_date_and_literal_transfer_stay(self, entries, _, options_map):
        """
        2013-06-03 * "Cash from ATM"
            Assets:Bank:Checking      -100 USD
                transaction-date: 2013-05-31
            Assets:Cash                 95 USD
            Expenses:Fee                 5 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"transaction-splitter",'
                      '  "metadata-name-date":"transaction-date",'
                      '  "transfer-account":"Liabilities:Bank:DebitCard",'
                      '  "dated-posting-move-mode":"stay"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "Cash from ATM"
            Liabilities:Bank:DebitCard     -100 USD
            Assets:Cash                      95 USD
            Expenses:Fee                      5 USD

        2013-06-03 * "Cash from ATM"
            Assets:Bank:Checking           -100 USD
            Liabilities:Bank:DebitCard      100 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_metadata_date_and_literal_transfer_move(self, entries, _, options_map):
        """
        2013-05-31 * "Cash from ATM"
            Assets:Bank:Checking      -100 USD
                booking-date: 2013-06-03
            Assets:Cash                 95 USD
            Expenses:Fee                 5 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"transaction-splitter",'
                      '  "metadata-name-date":"booking-date",'
                      '  "transfer-account":"Liabilities:Bank:DebitCard",'
                      '  "dated-posting-move-mode":"move"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "Cash from ATM"
            Liabilities:Bank:DebitCard     -100 USD
            Assets:Cash                      95 USD
            Expenses:Fee                      5 USD

        2013-06-03 * "Cash from ATM"
            Assets:Bank:Checking           -100 USD
            Liabilities:Bank:DebitCard      100 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_metadata_date_removed(self, entries, _, options_map):
        """
        2013-05-31 * "Paid by card"
            Assets:Bank:Checking      -100 USD
                booking-date: 2013-06-03
            Assets:Cash                100 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"transaction-splitter",'
                      '  "metadata-name-date":"booking-date",'
                      '  "transfer-account":"Liabilities:Bank:DebitCard",'
                      '  "dated-posting-move-mode":"move"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        for entry in new_entries:
            for posting in entry.postings:
                self.assertIsNone(posting.meta.get("booking-date") if posting.meta is not None else None, posting)

    @loader.load_doc(expect_errors=True)
    def test_metadata_date_and_literal_transfer_account_filter(self, entries, _, options_map):
        """
        2013-05-31 * "Paid by card 1"
            Assets:Bank:Checking1     -100 USD
                booking-date: 2013-06-03
            Assets:Cash                100 USD

        2013-06-12 * "Paid by card 2"
            Assets:Bank:Checking2     -200 USD
                booking-date: 2014-06-16
            Assets:Cash                200 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"transaction-splitter",'
                      '  "account":"Assets:Bank:Checking1",'
                      '  "metadata-name-date":"booking-date",'
                      '  "transfer-account":"Liabilities:Bank:DebitCard",'
                      '  "dated-posting-move-mode":"move"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "Paid by card 1"
            Liabilities:Bank:DebitCard     -100 USD
            Assets:Cash                     100 USD

        2013-06-03 * "Paid by card 1"
            Assets:Bank:Checking1          -100 USD
            Liabilities:Bank:DebitCard      100 USD

        2013-06-12 * "Paid by card 2"
            Assets:Bank:Checking2          -200 USD
                booking-date: 2014-06-16
            Assets:Cash                     200 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_metadata_date_and_metadata_transfer(self, entries, _, options_map):
        """
        2013-05-31 * "Paid by card"
            Assets:Bank:Checking      -100 USD
                booking-transfer-account: Assets:Bank:DebitCard
                booking-date: 2013-06-03
            Assets:Cash                100 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"transaction-splitter",'
                      '  "metadata-name-date":"booking-date",'
                      '  "metadata-name-transfer-account":"booking-transfer-account",'
                      '  "dated-posting-move-mode":"move"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "Paid by card"
            Assets:Bank:DebitCard     -100 USD
            Assets:Cash                100 USD

        2013-06-03 * "Paid by card"
            Assets:Bank:Checking      -100 USD
            Assets:Bank:DebitCard      100 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_metadata_transfer_removed(self, entries, _, options_map):
        """
        2013-05-31 * "Paid by card"
            Assets:Bank:Checking      -100 USD
                booking-transfer-account: Assets:Bank:DebitCard
                booking-date: 2013-06-03
            Assets:Cash                100 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"transaction-splitter",'
                      '  "metadata-name-date":"booking-date",'
                      '  "metadata-name-transfer-account":"booking-transfer-account",'
                      '  "dated-posting-move-mode":"move"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        for entry in new_entries:
            for posting in entry.postings:
                self.assertIsNone(posting.meta.get("booking-transfer-account") if posting.meta is not None else None,
                                  posting)

    @loader.load_doc(expect_errors=True)
    def test_metadata_date_and_literal_transfer_literal_stayed_narration(self, entries, _, options_map):
        """
        2013-06-03 * "Paid by card"
            Assets:Bank:Checking      -100 USD
                transfer-date: 2013-05-31
            Assets:Cash                100 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"transaction-splitter",'
                      '  "stayed-narration":"Custom narration",'
                      '  "metadata-name-date":"transfer-date",'
                      '  "transfer-account":"Assets:Bank:DebitCard",'
                      '  "dated-posting-move-mode":"stay"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "Paid by card"
            Assets:Bank:DebitCard     -100 USD
            Assets:Cash                100 USD

        2013-06-03 * "Custom narration"
            Assets:Bank:Checking      -100 USD
            Assets:Bank:DebitCard      100 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_metadata_date_and_literal_transfer_literal_moved_narration(self, entries, _, options_map):
        """
        2013-05-31 * "Paid by card"
            Assets:Bank:Checking      -100 USD
                booking-date: 2013-06-03
            Assets:Cash                100 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"transaction-splitter",'
                      '  "moved-narration":"Custom narration",'
                      '  "metadata-name-date":"booking-date",'
                      '  "transfer-account":"Assets:Bank:DebitCard",'
                      '  "dated-posting-move-mode":"move"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "Paid by card"
            Assets:Bank:DebitCard     -100 USD
            Assets:Cash                100 USD

        2013-06-03 * "Custom narration"
            Assets:Bank:Checking      -100 USD
            Assets:Bank:DebitCard      100 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_metadata_date_and_literal_transfer_metadata_moved_narration(self, entries, _, options_map):
        """
        2013-05-31 * "Paid by card"
            Assets:Bank:Checking      -100 USD
                booking-date: 2013-06-03
                narration: "Custom narration"
            Assets:Cash                100 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"transaction-splitter",'
                      '  "metadata-name-moved-narration":"narration",'
                      '  "metadata-name-date":"booking-date",'
                      '  "transfer-account":"Assets:Bank:DebitCard",'
                      '  "dated-posting-move-mode":"move"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "Paid by card"
            Assets:Bank:DebitCard     -100 USD
            Assets:Cash                100 USD

        2013-06-03 * "Custom narration"
            Assets:Bank:Checking      -100 USD
            Assets:Bank:DebitCard      100 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_metadata_narration_removed(self, entries, _, options_map):
        """
        2013-05-31 * "Paid by card"
            Assets:Bank:Checking      -100 USD
                booking-date: 2013-06-03
                narration: "Custom narration"
            Assets:Cash                100 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"transaction-splitter",'
                      '  "metadata-name-moved-narration":"narration",'
                      '  "metadata-name-date":"booking-date",'
                      '  "transfer-account":"Assets:Bank:DebitCard",'
                      '  "dated-posting-move-mode":"move"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        for entry in new_entries:
            for posting in entry.postings:
                self.assertIsNone(posting.meta.get("narration") if posting.meta is not None else None,
                                  posting)

    @loader.load_doc(expect_errors=True)
    def test_retain_payee(self, entries, _, options_map):
        """
        2013-05-31 * "The payee" "Paid by card"
            Assets:Bank:Checking      -100 USD
                booking-date: 2013-06-03
            Assets:Cash                100 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"transaction-splitter",'
                      '  "metadata-name-date":"booking-date",'
                      '  "transfer-account":"Assets:Bank:DebitCard",'
                      '  "dated-posting-move-mode":"move"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "The payee" "Paid by card"
            Assets:Bank:DebitCard     -100 USD
            Assets:Cash                100 USD

        2013-06-03 * "The payee" "Paid by card"
            Assets:Bank:Checking      -100 USD
            Assets:Bank:DebitCard      100 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_multiple_metadata_date_and_literal_transfer(self, entries, _, options_map):
        """
        2013-05-31 * "Paid for exam"
            Assets:Bank:Checking      -100 USD
            Expenses:Exams             40 USD
                exam-date: 2013-06-03
            Expenses:Exams             60 USD
                exam-date: 2013-06-03
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"transaction-splitter",'
                      '  "metadata-name-date":"exam-date",'
                      '  "transfer-account":"Assets:Receivables:Exams",'
                      '  "dated-posting-move-mode":"move"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "Paid for exam"
            Assets:Bank:Checking        -100 USD
            Assets:Receivables:Exams      40 USD
            Assets:Receivables:Exams      60 USD

        2013-06-03 * "Paid for exam"
            Assets:Receivables:Exams     -40 USD
            Expenses:Exams                40 USD

        2013-06-03 * "Paid for exam"
            Assets:Receivables:Exams     -60 USD
            Expenses:Exams                60 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_multiple_metadata_date_and_literal_transfer_and_metadata_narration(self, entries, _, options_map):
        """
        2013-05-31 * "Paid for exam"
            Assets:Bank:Checking      -100 USD
            Expenses:Exams             40 USD
                exam-date: 2013-06-03
                narration: "Custom narration"
            Expenses:Exams             60 USD
                exam-date: 2013-06-03
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"transaction-splitter",'
                      '  "metadata-name-date":"exam-date",'
                      '  "transfer-account":"Assets:Receivables:Exams",'
                      '  "metadata-name-moved-narration":"narration",'
                      '  "dated-posting-move-mode":"move"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "Paid for exam"
            Assets:Bank:Checking        -100 USD
            Assets:Receivables:Exams      40 USD
            Assets:Receivables:Exams      60 USD

        2013-06-03 * "Custom narration"
            Assets:Receivables:Exams     -40 USD
            Expenses:Exams                40 USD

        2013-06-03 * "Paid for exam"
            Assets:Receivables:Exams     -60 USD
            Expenses:Exams                60 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_multiple_rules_1(self, entries, _, options_map):
        """
        2013-05-31 * "Paid by card 1"
            Assets:Bank:Checking1     -100 USD
                booking-date: 2013-06-03
            Assets:Cash                100 USD

        2013-06-12 * "Paid by card 2"
            Assets:Bank:Checking2     -200 USD
                booking-date: 2014-06-16
            Assets:Cash                200 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type": "transaction-splitter",'
                      '  "dated-posting-move-mode": "stay",'
                      '  "metadata-name-date": "transaction-date",'
                      '  "metadata-name-transfer-account": "transfer-account"'
                      '},'
                      '{'
                      '  "type":"transaction-splitter",'
                      '  "account":"Assets:Bank:Checking1",'
                      '  "metadata-name-date":"booking-date",'
                      '  "transfer-account":"Liabilities:Bank:DebitCard",'
                      '  "dated-posting-move-mode":"move"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "Paid by card 1"
            Liabilities:Bank:DebitCard     -100 USD
            Assets:Cash                     100 USD

        2013-06-03 * "Paid by card 1"
            Assets:Bank:Checking1          -100 USD
            Liabilities:Bank:DebitCard      100 USD

        2013-06-12 * "Paid by card 2"
            Assets:Bank:Checking2          -200 USD
                booking-date: 2014-06-16
            Assets:Cash                     200 USD
        """,
            new_entries,
        )

    @loader.load_doc(expect_errors=True)
    def test_multiple_rules_2(self, entries, _, options_map):
        """
        2013-06-03 * "Paid by card 1"
            Assets:Bank:Checking1     -100 USD
                transaction-date: 2013-05-31
            Assets:Cash                100 USD

        2013-06-16 * "Paid by card 2"
            Assets:Bank:Checking2     -200 USD
                transaction-date: 2013-06-12
                transfer-account: Assets:Bank:DebitCard
            Assets:Cash                200 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type": "transaction-splitter",'
                      '  "dated-posting-move-mode": "stay",'
                      '  "metadata-name-date": "transaction-date",'
                      '  "metadata-name-transfer-account": "transfer-account"'
                      '},'
                      '{'
                      '  "type": "transaction-splitter",'
                      '  "dated-posting-move-mode": "stay",'
                      '  "account": "Assets:Bank:Checking1",'
                      '  "metadata-name-date": "transaction-date",'
                      '  "transfer-account": "Liabilities:Bank:DebitCard"'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulators(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "Paid by card 1"
            Liabilities:Bank:DebitCard     -100 USD
            Assets:Cash                     100 USD

        2013-06-03 * "Paid by card 1"
            Assets:Bank:Checking1          -100 USD
            Liabilities:Bank:DebitCard      100 USD

        2013-06-12 * "Paid by card 2"
            Assets:Bank:DebitCard          -200 USD
            Assets:Cash                     200 USD

        2013-06-16 * "Paid by card 2"
            Assets:Bank:Checking2          -200 USD
            Assets:Bank:DebitCard           200 USD
        """,
            new_entries,
        )


if __name__ == "__main__":
    unittest.main()
