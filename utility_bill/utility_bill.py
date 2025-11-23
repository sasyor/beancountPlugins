__plugins__ = ["utility_bill"]

import datetime
import json
from typing import List

from beancount.core import data
from dateutil.relativedelta import relativedelta


class UtilityBillFactory:
    @staticmethod
    def create(config_str):
        try:
            config = json.loads(config_str).get('utilities')
            return UtilityBill(config)
        except ValueError:
            return None


class UtilityBill:
    def __init__(self, utilities):
        self.utilities = utilities

    def replace(self, entries: List[data.Entries]):
        if self.utilities is None:
            return entries, []

        entries_result: List[data.Entries | data.Transaction] = []
        transactions_to_check: List[data.Transaction] = []

        for entry in entries:
            if isinstance(entry, data.Transaction):
                transactions_to_check.append(entry)
            else:
                entries_result.append(entry)

        for utility in self.utilities:
            remaining_transactions_to_check: List[data.Transaction] = transactions_to_check
            transactions_to_check = []
            transactions_to_process: List[data.Transaction] = []

            for transaction in remaining_transactions_to_check:
                if transaction.meta is not None and transaction.meta.get('utility-type') == utility['type']:
                    transactions_to_process.append(transaction)
                else:
                    transactions_to_check.append(transaction)

            for transaction in UtilitySpecificBill(utility).replace(transactions_to_process):
                entries_result.append(transaction)

        return entries_result


class UtilitySpecificBill:
    def __init__(self, utility):
        self.utility = utility

    def replace(self, transactions: List[data.Transaction]) -> list[data.Transaction]:
        entries_result: List[data.Transaction] = []

        for transaction in transactions:
            entries_result.extend(self.distribute_transaction(transaction))

        return entries_result

    def distribute_transaction(self, txn: data.Transaction) -> list[data.Transaction]:
        entries_result = []
        transfer_account = 'Assets:Utilities:Electricity'

        entries_result.append(self.create_parent_txn(txn, transfer_account))

        period_start: datetime.date = txn.meta.get('period-start')
        period_end: datetime.date = txn.meta.get('period-end')

        base_amount = self.get_base_amount(txn.postings, period_start, period_end)

        monthly_start = period_start
        monthly_end = period_start + relativedelta(day=1, months=1) - relativedelta(days=1)

        while monthly_start <= period_end:
            if monthly_end.month == period_end.month:
                monthly_end = period_end

            if monthly_end.month == period_start.month:
                monthly_days = monthly_end.day - monthly_start.day
            elif monthly_end.month == period_end.month:
                monthly_days = period_end.day
            else:
                monthly_days = monthly_end.day

            entries_result.append(
                self.create_child_txn(txn, transfer_account, monthly_days, monthly_end, base_amount))

            monthly_start += relativedelta(day=1, months=1)
            monthly_end += relativedelta(day=1, months=2) - relativedelta(days=1)

        return entries_result

    @staticmethod
    def create_parent_txn(txn: data.Transaction, transfer_account: data.Account) -> data.Transaction:
        postings = []
        for posting in txn.postings:
            if posting.account == 'Expenses:Utilities:Electricity':
                postings.append(data.Posting(transfer_account,
                                             posting.units,
                                             posting.cost,
                                             posting.price,
                                             posting.flag,
                                             posting.meta))
            else:
                postings.append(posting)

        return data.Transaction(txn.meta,
                                txn.date,
                                txn.flag,
                                txn.payee,
                                txn.narration,
                                txn.tags,
                                txn.links, postings)

    @staticmethod
    def create_child_txn(txn: data.Transaction, transfer_account: data.Account, days: int, date: datetime.date,
                         base_amount) -> data.Transaction:
        txn = data.Transaction(data.new_metadata(txn.meta['filename'], txn.meta['lineno']),
                               date,
                               txn.flag,
                               txn.payee,
                               txn.narration,
                               txn.tags,
                               txn.links, [])

        amount = round(days * base_amount)
        data.create_simple_posting(txn, transfer_account, -amount, 'HUF')
        data.create_simple_posting(txn, 'Expenses:Utilities:Electricity', amount, 'HUF')

        return txn

    @staticmethod
    def get_base_amount(postings: List[data.Posting], start: datetime.date, end: datetime.date) -> int:
        units = None
        days = (end - start).days
        for posting in postings:
            if posting.account == 'Expenses:Utilities:Electricity':
                units = posting.units
                break

        return 0 if units is None else units.number / days


utility_bill_factory_obj = UtilityBillFactory()


def utility_bill(entries, options_map, config_str=""):
    utility_bill_obj = utility_bill_factory_obj.create(config_str)
    return utility_bill_obj.replace(entries) if utility_bill_obj is not None else entries, []
