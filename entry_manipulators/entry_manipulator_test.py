import unittest

from beancount import loader
from beancount.parser import cmptest

from entry_manipulator_orchestrator import entry_manipulator


class TestTxnSplitter(cmptest.TestCase):

    # @loader.load_doc(expect_errors=True)
    # def test_metadata_retention(self, entries, _, options_map):
    #     """
    #     2013-05-31 * "Paid by card"
    #         random-1: "text-1"
    #         Assets:Bank:Checking      -100 USD
    #             booking-date: 2013-06-03
    #             random-2: "text-2"
    #         Assets:Cash                100 USD
    #             random-3: "text-3"
    #     """
    #     config_str = ('{'
    #                   '"metadata-name-date":"booking-date",'
    #                   '"transfer-account":"Assets:Bank:DebitCard"'
    #                   '}')
    #     new_entries, _ = entry_manipulator(entries, options_map, config_str)
    #
    #     for entry in new_entries:
    #         self.assertEqual(entry.meta.get("random-1"), "text-1", entry)
    #         for posting in entry.postings:
    #             if posting.account == "Assets:Bank:Checking":
    #                 self.assertEqual(posting.meta.get("random-2"), "text-2", posting)
    #                 self.assertIsNone(posting.meta.get("random-3"), posting)
    #             if posting.account == "Assets:Cash":
    #                 self.assertIsNone(posting.meta.get("random-2"), posting)
    #                 self.assertEqual(posting.meta.get("random-3"), "text-3", posting)
    #
    @loader.load_doc(expect_errors=True)
    def test_metadata_date_and_literal_transfer(self, entries, _, options_map):
        """
        2013-06-03 * "Paid by card"
            Assets:Bank:Checking      -100 USD
                transaction-date: 2013-05-31
            Assets:Cash                100 USD
        """
        config_str = ('{"manipulators": ['
                      '{'
                      '  "type":"transaction-splitter",'
                      '  "metadata-name-date":"transaction-date",'
                      '  "transfer-account":"Liabilities:Bank:DebitCard",'
                      '  "inverted-date-mode":True'
                      '}'
                      ']}')
        new_entries, _ = entry_manipulator(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2013-05-31 * "Paid by card"
            Liabilities:Bank:DebitCard     -100 USD
            Assets:Cash                     100 USD

        2013-06-03 * "Paid by card"
            Assets:Bank:Checking           -100 USD
            Liabilities:Bank:DebitCard      100 USD
        """,
            new_entries,
        )

    # @loader.load_doc(expect_errors=True)
    # def test_metadata_date_removed(self, entries, _, options_map):
    #     """
    #     2013-05-31 * "Paid by card"
    #         Assets:Bank:Checking      -100 USD
    #             booking-date: 2013-06-03
    #         Assets:Cash                100 USD
    #     """
    #     config_str = ('{'
    #                   '"metadata-name-date":"booking-date",'
    #                   '"transfer-account":"Assets:Bank:DebitCard"'
    #                   '}')
    #     new_entries, _ = txn_splitter(entries, options_map, config_str)
    #
    #     for entry in new_entries:
    #         for posting in entry.postings:
    #             self.assertIsNone(posting.meta.get("booking-date") if posting.meta is not None else None, posting)
    #
    # @loader.load_doc(expect_errors=True)
    # def test_metadata_date_and_literal_transfer_account_filter(self, entries, _, options_map):
    #     """
    #     2013-05-31 * "Paid by card 1"
    #         Assets:Bank:Checking1     -100 USD
    #             booking-date: 2013-06-03
    #         Assets:Cash                100 USD
    #
    #     2013-06-12 * "Paid by card 2"
    #         Assets:Bank:Checking2     -200 USD
    #             booking-date: 2014-06-16
    #         Assets:Cash                200 USD
    #     """
    #     config_str = ('{'
    #                   '"account":"Assets:Bank:Checking1",'
    #                   '"metadata-name-date":"booking-date",'
    #                   '"transfer-account":"Assets:Bank:DebitCard"'
    #                   '}')
    #     new_entries, _ = txn_splitter(entries, options_map, config_str)
    #
    #     self.assertEqualEntries(
    #         """
    #     2013-05-31 * "Paid by card 1"
    #         Assets:Bank:DebitCard     -100 USD
    #         Assets:Cash                100 USD
    #
    #     2013-06-03 * "Paid by card 1"
    #         Assets:Bank:Checking1     -100 USD
    #         Assets:Bank:DebitCard      100 USD
    #
    #     2013-06-12 * "Paid by card 2"
    #         Assets:Bank:Checking2     -200 USD
    #             booking-date: 2014-06-16
    #         Assets:Cash                200 USD
    #     """,
    #         new_entries,
    #     )
    #
    # @loader.load_doc(expect_errors=True)
    # def test_metadata_date_and_metadata_transfer(self, entries, _, options_map):
    #     """
    #     2013-05-31 * "Paid by card"
    #         Assets:Bank:Checking      -100 USD
    #             booking-transfer-account: Assets:Bank:DebitCard
    #             booking-date: 2013-06-03
    #         Assets:Cash                100 USD
    #     """
    #     config_str = ('{'
    #                   '"metadata-name-date":"booking-date",'
    #                   '"metadata-name-transfer-account":"booking-transfer-account"'
    #                   '}')
    #     new_entries, _ = txn_splitter(entries, options_map, config_str)
    #
    #     self.assertEqualEntries(
    #         """
    #     2013-05-31 * "Paid by card"
    #         Assets:Bank:DebitCard     -100 USD
    #         Assets:Cash                100 USD
    #
    #     2013-06-03 * "Paid by card"
    #         Assets:Bank:Checking      -100 USD
    #         Assets:Bank:DebitCard      100 USD
    #     """,
    #         new_entries,
    #     )
    #
    # @loader.load_doc(expect_errors=True)
    # def test_metadata_transfer_removed(self, entries, _, options_map):
    #     """
    #     2013-05-31 * "Paid by card"
    #         Assets:Bank:Checking      -100 USD
    #             booking-transfer-account: Assets:Bank:DebitCard
    #             booking-date: 2013-06-03
    #         Assets:Cash                100 USD
    #     """
    #     config_str = ('{'
    #                   '"metadata-name-date":"booking-date",'
    #                   '"metadata-name-transfer-account":"booking-transfer-account"'
    #                   '}')
    #     new_entries, _ = txn_splitter(entries, options_map, config_str)
    #
    #     for entry in new_entries:
    #         for posting in entry.postings:
    #             self.assertIsNone(posting.meta.get("booking-transfer-account") if posting.meta is not None else None,
    #                               posting)
    #
    # @loader.load_doc(expect_errors=True)
    # def test_metadata_date_and_literal_transfer_literal_narration(self, entries, _, options_map):
    #     """
    #     2013-05-31 * "Paid by card"
    #         Assets:Bank:Checking      -100 USD
    #             booking-date: 2013-06-03
    #         Assets:Cash                100 USD
    #     """
    #     config_str = ('{'
    #                   '"metadata-name-date":"booking-date",'
    #                   '"transfer-account":"Assets:Bank:DebitCard",'
    #                   '"narration":"Custom narration"'
    #                   '}')
    #     new_entries, _ = txn_splitter(entries, options_map, config_str)
    #
    #     self.assertEqualEntries(
    #         """
    #     2013-05-31 * "Paid by card"
    #         Assets:Bank:DebitCard     -100 USD
    #         Assets:Cash                100 USD
    #
    #     2013-06-03 * "Custom narration"
    #         Assets:Bank:Checking      -100 USD
    #         Assets:Bank:DebitCard      100 USD
    #     """,
    #         new_entries,
    #     )
    #
    # @loader.load_doc(expect_errors=True)
    # def test_metadata_date_and_literal_transfer_metadata_narration(self, entries, _, options_map):
    #     """
    #     2013-05-31 * "Paid by card"
    #         Assets:Bank:Checking      -100 USD
    #             booking-date: 2013-06-03
    #             narration: "Custom narration"
    #         Assets:Cash                100 USD
    #     """
    #     config_str = ('{'
    #                   '"metadata-name-date":"booking-date",'
    #                   '"transfer-account":"Assets:Bank:DebitCard",'
    #                   '"metadata-name-narration":"narration"'
    #                   '}')
    #     new_entries, _ = txn_splitter(entries, options_map, config_str)
    #
    #     self.assertEqualEntries(
    #         """
    #     2013-05-31 * "Paid by card"
    #         Assets:Bank:DebitCard     -100 USD
    #         Assets:Cash                100 USD
    #
    #     2013-06-03 * "Custom narration"
    #         Assets:Bank:Checking      -100 USD
    #         Assets:Bank:DebitCard      100 USD
    #     """,
    #         new_entries,
    #     )
    #
    # @loader.load_doc(expect_errors=True)
    # def test_metadata_narration_removed(self, entries, _, options_map):
    #     """
    #     2013-05-31 * "Paid by card"
    #         Assets:Bank:Checking      -100 USD
    #             booking-date: 2013-06-03
    #             narration: "Custom narration"
    #         Assets:Cash                100 USD
    #     """
    #     config_str = ('{'
    #                   '"metadata-name-date":"booking-date",'
    #                   '"transfer-account":"Assets:Bank:DebitCard",'
    #                   '"metadata-name-narration":"narration"'
    #                   '}')
    #     new_entries, _ = txn_splitter(entries, options_map, config_str)
    #
    #     for entry in new_entries:
    #         for posting in entry.postings:
    #             self.assertIsNone(posting.meta.get("narration") if posting.meta is not None else None,
    #                               posting)
    #
    # @loader.load_doc(expect_errors=True)
    # def test_retain_payee(self, entries, _, options_map):
    #     """
    #     2013-05-31 * "The payee" "Paid by card"
    #         Assets:Bank:Checking      -100 USD
    #             booking-date: 2013-06-03
    #         Assets:Cash                100 USD
    #     """
    #     config_str = ('{'
    #                   '"metadata-name-date":"booking-date",'
    #                   '"transfer-account":"Assets:Bank:DebitCard",'
    #                   '}')
    #     new_entries, _ = txn_splitter(entries, options_map, config_str)
    #
    #     self.assertEqualEntries(
    #         """
    #     2013-05-31 * "The payee" "Paid by card"
    #         Assets:Bank:DebitCard     -100 USD
    #         Assets:Cash                100 USD
    #
    #     2013-06-03 * "The payee" "Paid by card"
    #         Assets:Bank:Checking      -100 USD
    #         Assets:Bank:DebitCard      100 USD
    #     """,
    #         new_entries,
    #     )
    #
    # @loader.load_doc(expect_errors=True)
    # def test_multiple_metadata_date_and_literal_transfer(self, entries, _, options_map):
    #     """
    #     2013-05-31 * "Paid for exam"
    #         Assets:Bank:Checking      -100 USD
    #         Expenses:Exams             40 USD
    #             exam-date: 2013-06-03
    #         Expenses:Exams             60 USD
    #             exam-date: 2013-06-03
    #     """
    #     config_str = ('{'
    #                   '"metadata-name-date":"exam-date",'
    #                   '"transfer-account":"Assets:Receivables:Exams"'
    #                   '}')
    #     new_entries, _ = txn_splitter(entries, options_map, config_str)
    #
    #     self.assertEqualEntries(
    #         """
    #     2013-05-31 * "Paid for exam"
    #         Assets:Bank:Checking        -100 USD
    #         Assets:Receivables:Exams      40 USD
    #         Assets:Receivables:Exams      60 USD
    #
    #     2013-06-03 * "Paid for exam"
    #         Assets:Receivables:Exams     -40 USD
    #         Expenses:Exams                40 USD
    #
    #     2013-06-03 * "Paid for exam"
    #         Assets:Receivables:Exams     -60 USD
    #         Expenses:Exams                60 USD
    #     """,
    #         new_entries,
    #     )
    #
    # @loader.load_doc(expect_errors=True)
    # def test_multiple_metadata_date_and_literal_transfer_and_metadata_narration(self, entries, _, options_map):
    #     """
    #     2013-05-31 * "Paid for exam"
    #         Assets:Bank:Checking      -100 USD
    #         Expenses:Exams             40 USD
    #             exam-date: 2013-06-03
    #             narration: "Custom narration"
    #         Expenses:Exams             60 USD
    #             exam-date: 2013-06-03
    #     """
    #     config_str = ('{'
    #                   '"metadata-name-date":"exam-date",'
    #                   '"transfer-account":"Assets:Receivables:Exams",'
    #                   '"metadata-name-narration":"narration"'
    #                   '}')
    #     new_entries, _ = txn_splitter(entries, options_map, config_str)
    #
    #     self.assertEqualEntries(
    #         """
    #     2013-05-31 * "Paid for exam"
    #         Assets:Bank:Checking        -100 USD
    #         Assets:Receivables:Exams      40 USD
    #         Assets:Receivables:Exams      60 USD
    #
    #     2013-06-03 * "Custom narration"
    #         Assets:Receivables:Exams     -40 USD
    #         Expenses:Exams                40 USD
    #
    #     2013-06-03 * "Paid for exam"
    #         Assets:Receivables:Exams     -60 USD
    #         Expenses:Exams                60 USD
    #     """,
    #         new_entries,
    #     )
    #
    # @loader.load_doc(expect_errors=True)
    # def test_metadata_date_and_literal_transfer_and_inverted_date_mode(self, entries, _, options_map):
    #     """
    #     2013-06-03 * "Exams"
    #         Assets:Bank:Checking      -100 USD
    #             exams-date: 2013-05-31
    #         Expenses:Exams               30 USD
    #         Expenses:Exams               70 USD
    #     """
    #     config_str = ('{'
    #                   '"metadata-name-date":"exams-date",'
    #                   '"transfer-account":"Liabilities:Learning",'
    #                   '"inverted-date-mode":True'
    #                   '}')
    #     new_entries, _ = txn_splitter(entries, options_map, config_str)
    #
    #     self.assertEqualEntries(
    #         """
    #     2013-05-31 * "Exams"
    #         Liabilities:Learning       -100 USD
    #         Expenses:Exams               30 USD
    #         Expenses:Exams               70 USD
    #
    #     2013-06-03 * "Exams"
    #         Assets:Bank:Checking       -100 USD
    #         Liabilities:Learning        100 USD
    #     """,
    #         new_entries,
    #     )


if __name__ == "__main__":
    unittest.main()
