import ast
import collections
import copy

from beancount.core import data

__plugins__ = ["txn_splitter"]

SplitCardTransactionError = collections.namedtuple(
    "SplitCardTransactionError", "source message entry"
)


class TxnSplitter:

    def split(self, entries, options_map, config_str=""):
        config = {}
        expr = ast.literal_eval(config_str)
        config.update(expr)

        new_entries = []

        for entry in entries:

            if not isinstance(entry, data.Transaction):
                continue

            new_txn = self.__try_create_txn(config, entry)
            if new_txn is not None:
                new_entries.append(new_txn)

        return entries + new_entries, []

    def __try_create_txn(self, rule, entry):
        metadata_name_date = rule["metadata-name-date"]
        metadata_names_to_remove = [metadata_name_date]

        relevant_postings_filters = [lambda posting: posting.meta and metadata_name_date in posting.meta]
        if "metadata-name-transfer-account" in rule:
            metadata_name_transfer_account = rule["metadata-name-transfer-account"]
            relevant_postings_filters.append(lambda posting: metadata_name_transfer_account in posting.meta)
            transfer_account_get = lambda posting: posting.meta[
                metadata_name_transfer_account
            ]
            metadata_names_to_remove.append(metadata_name_transfer_account)
        elif "transfer-account" in rule:
            if "account" in rule:
                relevant_postings_filters.append(lambda posting: posting.account == rule["account"])
            transfer_account_get = lambda posting: rule["transfer-account"]
        else:
            return None

        relevant_postings = list(
            filter(
                lambda posting: all(f(posting) for f in relevant_postings_filters),
                entry.postings,
            )
        )
        if len(relevant_postings) != 1:
            return None

        relevant_posting = relevant_postings[0]
        transfer_account = transfer_account_get(relevant_posting)

        date = self.__get_date(relevant_posting, metadata_name_date)
        narration = self.__get_narration(entry, rule)
        self.__modify_existing_txn(entry, relevant_posting, transfer_account, metadata_names_to_remove)
        return self.__create_new_txn(
            entry,
            relevant_posting,
            date,
            narration,
            transfer_account,
        )

    @staticmethod
    def __get_date(relevant_posting, metadata_name_date):
        return relevant_posting.meta[metadata_name_date]

    @staticmethod
    def __get_narration(entry, rule):
        narration = rule.get("narration")
        if narration is None:
            narration = entry.narration
        return narration

    @staticmethod
    def __modify_existing_txn(entry, relevant_posting, transfer_account, metadata_names_to_remove):
        for metadata_name_to_remove in metadata_names_to_remove:
            del relevant_posting.meta[metadata_name_to_remove]

        entry.postings.remove(relevant_posting)
        data.create_simple_posting(
            entry,
            transfer_account,
            relevant_posting.units.number,
            relevant_posting.units.currency,
        )

    @staticmethod
    def __create_new_txn(entry, relevant_posting, date, narration, transfer_account):
        # create new txn
        new_txn = copy.deepcopy(entry)
        new_txn = new_txn._replace(
            narration=narration,
            date=date,
            postings=[copy.deepcopy(relevant_posting)],
        )
        data.create_simple_posting(
            new_txn,
            transfer_account,
            -relevant_posting.units.number,
            relevant_posting.units.currency,
        )

        return new_txn


txn_splitter_obj = TxnSplitter()


def txn_splitter(entries, options_map, config_str=""):
    return txn_splitter_obj.split(entries, options_map, config_str)
