from beancount import loader
from beancount.parser import cmptest

from utility_bill.utility_bill import utility_bill


class TestUtilityBill(cmptest.TestCase):

    @loader.load_doc(expect_errors=True)
    def test_1_pre_invoice_only_payment_date(self, entries, _, options_map):
        """
        2024-10-28 * "Villany - részszámla"
            Assets:Bank                   -6,671 HUF
                invoice-date: 2024-10-25
            Expenses:Electricity:Prepaid   6,671 HUF
                start: 2024-09-23
                end: 2024-10-22
        """
        config_str = ('{"utilities": ['
                      '{'
                      '  "type":"electricity",'
                      '  "transfer-account":"Assets:Utilities:Electricity",'
                      '  "estimated-account":"Expenses:Utilities:Electricity:Estimated",'
                      '  "actual-account":"Expenses:Utilities:Electricity:Actual"'
                      '}'
                      ']}')
        new_entries, _ = utility_bill(entries, options_map, config_str)

        self.assertEqualEntries(
            """
        2024-09-30 * "Villany - fogyasztás (2024-09-23 - 2024-09-30)"
            Liabilities:Electricity           -1,779 HUF
            Expenses:Electricity:Prepaid       1,779 HUF
        
        2024-10-22 * "Villany - fogyasztás (2024-10-01 - 2024-10-22)"
            Liabilities:Electricity           -4,892 HUF
            Expenses:Electricity:Prepaid       4,892 HUF
        
        2024-10-28 * "Villany - részszámla"
            Assets:Bank                       -6,671 HUF
            Liabilities:Electricity            6,671 HUF
        """,
            new_entries,
        )
