import ast
import datetime

__plugins__ = ["balance_pad_creator"]

from beancount.core import data
from beancount.core.data import Balance


class BalancePadCreator:
    def create(self, entries, options_map, config_str=""):
        config = {}
        expr = ast.literal_eval(config_str)
        config.update(expr)

        account = config["account"]
        metadata_name_balance_unit = config["metadata-name-balance-unit"]
        metadata_name_balance_time = config["metadata-name-balance-time"]

        non_relevant_entries = []
        relevant_balances = {}
        for entry in entries:
            if isinstance(entry, Balance) and entry.account == account:
                self.update_relevant_balances(entry, relevant_balances)
                continue

            non_relevant_entries.append(entry)
            relevant_postings = list(
                filter(lambda
                           posting: posting.account == account and posting.meta and metadata_name_balance_unit in posting.meta,
                       entry.postings))

            if len(relevant_postings) == 0:
                continue

            for new_balance in self.__create_balances(entry, metadata_name_balance_time, metadata_name_balance_unit,
                                                      relevant_postings):
                self.update_relevant_balances(new_balance, relevant_balances)

        return non_relevant_entries + list(relevant_balances.values()), []

    @staticmethod
    def update_relevant_balances(entry, relevant_balances):
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


balance_pad_creator_obj = BalancePadCreator()


def balance_pad_creator(entries, options_map, config_str=""):
    return balance_pad_creator_obj.create(entries, options_map, config_str)
