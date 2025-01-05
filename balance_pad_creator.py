import ast
import datetime

__plugins__ = ["balance_pad_creator"]

from beancount.core import data
from beancount.core.data import Balance, Transaction
from beancount.ops.pad import pad


class BalancePadCreator:
    def create(self, entries, options_map, config_str="", skip_padding=False):
        config = {}
        expr = ast.literal_eval(config_str)
        config.update(expr)

        account = config["account"]
        metadata_name_balance_unit = config["metadata-name-balance-unit"]
        metadata_name_balance_time = config["metadata-name-balance-time"]

        non_relevant_entries = []
        relevant_balances = {}
        relevant_txs = []
        for entry in entries:
            if isinstance(entry, Balance) and entry.account == account:
                self.__update_relevant_balances(entry, relevant_balances)
                continue

            if not isinstance(entry, Transaction):
                non_relevant_entries.append(entry)
                continue

            relevant_txs.append(entry)
            relevant_postings = list(
                filter(lambda
                           posting: posting.account == account and posting.meta and metadata_name_balance_unit in posting.meta,
                       entry.postings))

            if len(relevant_postings) == 0:
                continue

            for new_balance in self.__create_balances(entry, metadata_name_balance_time, metadata_name_balance_unit,
                                                      relevant_postings):
                self.__update_relevant_balances(new_balance, relevant_balances)

        pads = self.__create_pads(account, config, relevant_balances, relevant_txs)

        errors = []
        entries_for_padding = list(relevant_balances.values()) + relevant_txs + pads
        if skip_padding:
            (entries_after_pad, errors) = pad(entries_for_padding, options_map)
        else:
            entries_after_pad = entries_for_padding
        return non_relevant_entries + entries_after_pad, errors

    @staticmethod
    def __update_relevant_balances(entry, relevant_balances):
        relevant_balance = relevant_balances.get(entry.date)
        metadata_name_time = "balance-time"
        if not relevant_balance:
            relevant_balances[entry.date] = entry
        elif relevant_balance and relevant_balance.meta[metadata_name_time] < entry.meta[metadata_name_time]:
            relevant_balances[entry.date] = entry

    @staticmethod
    def __create_balances(entry, metadata_name_balance_time, metadata_name_balance_unit, relevant_postings):
        new_entries = []
        for posting in relevant_postings:
            date = entry.date + datetime.timedelta(days=1)
            units = posting.meta[metadata_name_balance_unit]
            meta = {metadata_name_balance_time: posting.meta[metadata_name_balance_time]}
            balance = data.Balance(
                data.new_metadata(entry.meta["filename"], entry.meta["lineno"], meta), date, posting.account,
                units, None, None
            )
            new_entries.append(balance)
        return new_entries

    @staticmethod
    def __create_pads(account, config, relevant_balances, relevant_txs):
        pads = []
        previous_balance = None
        sorted_balance_dates = sorted(balance.date for balance in relevant_balances.values())
        for balance_date in sorted_balance_dates:
            balance = relevant_balances[balance_date]

            txn_amount = previous_balance.amount.number if previous_balance else 0
            for txn in relevant_txs:
                if txn.date >= balance_date:
                    continue
                if previous_balance and txn.date < previous_balance.date:
                    continue
                for posting in txn.postings:
                    if posting.account == account:
                        txn_amount += posting.units.number

            if txn_amount != balance.amount.number:
                date = balance.date + datetime.timedelta(days=-1)
                pads.append(data.Pad(data.new_metadata(balance.meta["filename"], balance.meta["lineno"]), date, account,
                                     config["pad-account"]))

            previous_balance = balance
        return pads


balance_pad_creator_obj = BalancePadCreator()


def balance_pad_creator(entries, options_map, config_str=""):
    return balance_pad_creator_obj.create(entries, options_map, config_str)


def balance_pad_creator_testable(entries, options_map, config_str=""):
    return balance_pad_creator_obj.create(entries, options_map, config_str, True)
