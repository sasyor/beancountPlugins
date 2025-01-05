import ast
import datetime

__plugins__ = ["balance_pad_creator"]

from beancount.parser import grammar


class BalancePadCreator:
    def create(self, entries, options_map, config_str=""):
        config = {}
        expr = ast.literal_eval(config_str)
        config.update(expr)

        metadata_name_balance_unit = config["metadata-name-balance-unit"]
        metadata_name_balance_time = config["metadata-name-balance-time"]

        new_entries = []
        for entry in entries:
            relevant_postings = list(
                filter(lambda posting: posting.meta and metadata_name_balance_unit in posting.meta, entry.postings))
            if len(relevant_postings) == 0:
                continue
            for new_entry in self.__create_entries(entry, metadata_name_balance_time, metadata_name_balance_unit,
                                                   relevant_postings):
                new_entries.append(new_entry)

        return entries + new_entries, []

    @staticmethod
    def __create_entries(entry, metadata_name_balance_time, metadata_name_balance_unit, relevant_postings):
        builder = grammar.Builder()
        new_entries = []
        for posting in relevant_postings:
            date = entry.date + datetime.timedelta(days=1)
            units = posting.meta[metadata_name_balance_unit]
            meta = {metadata_name_balance_time: posting.meta[metadata_name_balance_time]}
            balance = builder.balance(entry.meta["filename"], entry.meta["lineno"], date, posting.account, units,
                                      None, meta)
            new_entries.append(balance)
        return new_entries


balance_pad_creator_obj = BalancePadCreator()


def balance_pad_creator(entries, options_map, config_str=""):
    return balance_pad_creator_obj.create(entries, options_map, config_str)
