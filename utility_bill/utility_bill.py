__plugins__ = ["utility_bill"]

import datetime

from beancount.core import data
from dateutil.relativedelta import relativedelta


class UtilityBill:
    def replace(self, entries):
        entries_result = []

        for entry in entries:
            if not isinstance(entry, data.Transaction) or entry.meta is None or entry.meta.get(
                    'utility-type') != 'electricity':
                entries_result.append(entry)
                continue

            entries_result.extend(self.distribute_transaction(entry))

        return entries_result

    def distribute_transaction(self, entry: data.Transaction):
        entries_result = []
        transfer_account = 'Assets:Utilities:Electricity'

        entries_result.append(self.create_parent_txn(entry, transfer_account))

        period_start = entry.meta.get('period-start')
        period_end = entry.meta.get('period-end')

        base_amount = self.get_base_amount(entry, period_start, period_end)

        monthly_start = period_start
        monthly_end = period_start + relativedelta(day=1, months=1) - relativedelta(days=1)

        while monthly_start <= period_end:
            if monthly_end.month == period_end.month:
                monthly_days = period_end.day
                monthly_end = period_end
            else:
                monthly_days = monthly_end.day - monthly_start.day

            entries_result.append(
                self.create_child_txn(entry, transfer_account, monthly_days, monthly_end, base_amount))

            if monthly_start.month == period_start.month:
                monthly_start = datetime.date(period_start.year, period_start.month, 1)
            monthly_start += relativedelta(months=1)
            monthly_end += relativedelta(months=1)

        return entries_result

    @staticmethod
    def create_parent_txn(entry, transfer_account):
        postings = []
        for posting in entry.postings:
            if posting.account == 'Expenses:Utilities:Electricity':
                postings.append(data.Posting(transfer_account,
                                             posting.units,
                                             posting.cost,
                                             posting.price,
                                             posting.flag,
                                             posting.meta))
            else:
                postings.append(posting)

        return data.Transaction(entry.meta,
                                entry.date,
                                entry.flag,
                                entry.payee,
                                entry.narration,
                                entry.tags,
                                entry.links, postings)

    @staticmethod
    def create_child_txn(entry, transfer_account, days, date, base_amount):
        txn = data.Transaction(data.new_metadata(entry.meta['filename'], entry.meta['lineno']),
                               date,
                               entry.flag,
                               entry.payee,
                               entry.narration,
                               entry.tags,
                               entry.links, [])

        amount = round(days * base_amount)
        data.create_simple_posting(txn, transfer_account, -amount, 'HUF')
        data.create_simple_posting(txn, 'Expenses:Utilities:Electricity', amount, 'HUF')

        return txn

    @staticmethod
    def get_base_amount(entry, start, end):
        units = None
        days = (end - start).days
        for posting in entry.postings:
            if posting.account == 'Expenses:Utilities:Electricity':
                units = posting.units
                break

        return 0 if units is None else units.number / days


utility_bill_obj = UtilityBill()


def utility_bill(entries, options_map, config_str=""):
    return utility_bill_obj.replace(entries), []
