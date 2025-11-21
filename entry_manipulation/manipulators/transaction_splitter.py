import re

from beancount.core import data

from ..data.entry_manipulation_result_data import EntryManipulationResultData
from ..entry_manipulator_base import EntryManipulatorBase


class TransactionSplitter(EntryManipulatorBase):
    def __init__(self, config):
        super().__init__(config)

        self.metadata_name_date = config["metadata-name-date"]
        self.metadata_name_transfer_account = config.get("metadata-name-transfer-account")

        self.transfer_account_get = None
        if self.metadata_name_transfer_account is not None:
            self.transfer_account_get = lambda p: p.meta.get(
                self.metadata_name_transfer_account
            )
        elif "transfer-account" in self.config:
            self.transfer_account_get = lambda _: self.config["transfer-account"]

    def execute(self, entry: data.Transaction) -> EntryManipulationResultData:
        metadata_names_to_remove = {self.metadata_name_date}

        if self.metadata_name_transfer_account is not None:
            metadata_names_to_remove.add(self.metadata_name_transfer_account)
        elif "transfer-account" in self.config:
            pass
        else:
            return EntryManipulationResultData([entry])

        transactions_to_return = []
        entries_to_process = [entry]
        while len(entries_to_process) > 0:
            main_txn = entries_to_process.pop(0)
            new_transactions = self.__process_entry(main_txn, metadata_names_to_remove)
            if new_transactions is None:
                transactions_to_return.append(main_txn)
            else:
                for new_transaction in new_transactions:
                    entries_to_process.append(new_transaction)

        return EntryManipulationResultData(transactions_to_return)

    def __process_entry(self, main_txn, metadata_names_to_remove):
        for main_posting in main_txn.postings:
            new_transactions = self.__process_posting(main_txn, main_posting, metadata_names_to_remove)
            if new_transactions is not None:
                return new_transactions

        return None

    def __process_posting(self, entry, main_posting, metadata_names_to_remove):
        dated_posting_move_mode = self.config["dated-posting-move-mode"]

        if not main_posting.meta or not self.metadata_name_date in main_posting.meta:
            return None
        if "account" in self.config and not re.search(self.config["account"], main_posting.account):
            return None

        (stayed_narration, moved_narration, metadata_name_to_remove) = self.__get_narration(entry, main_posting)
        if metadata_name_to_remove:
            metadata_names_to_remove.add(metadata_name_to_remove)

        modified_main_posting = self.__get_main_posting_copy(main_posting, metadata_names_to_remove)
        other_postings = list(filter(lambda p: p != main_posting, entry.postings))

        transfer_account = self.transfer_account_get(main_posting)
        if transfer_account is None:
            return None

        if dated_posting_move_mode == "stay":
            postings_for_original_txn = [modified_main_posting,
                                         self.__create_transfer_posting(main_posting, transfer_account, True)]
            postings_for_new_txn = other_postings
            postings_for_new_txn.append(self.__create_transfer_posting(main_posting, transfer_account, False))
        elif dated_posting_move_mode == "move":
            postings_for_original_txn = other_postings
            postings_for_original_txn.append(self.__create_transfer_posting(main_posting, transfer_account, False))
            postings_for_new_txn = [modified_main_posting,
                                    self.__create_transfer_posting(main_posting, transfer_account, True)]
        else:
            return None

        new_transactions = [self.__recreate_existing_txn(entry, postings_for_original_txn, stayed_narration)]

        date = self.__get_date(main_posting)
        new_transactions.append(self.__create_new_txn(
            entry,
            postings_for_new_txn,
            date,
            moved_narration,
        ))
        return new_transactions

    def __get_date(self, relevant_posting):
        return relevant_posting.meta[self.metadata_name_date]

    @staticmethod
    def __get_main_posting_copy(main_posting, metadata_names_to_remove):
        meta = {}
        for key in main_posting.meta:
            if key not in metadata_names_to_remove:
                meta[key] = main_posting.meta[key]

        return data.Posting(main_posting.account, main_posting.units, main_posting.cost,
                            main_posting.price, main_posting.flag, meta)

    def __get_narration(self, entry, relevant_posting):
        stayed_narration = self.config.get("stayed-narration")
        moved_narration = self.config.get("moved-narration")
        metadata_name_moved_narration = self.config.get("metadata-name-moved-narration")
        if metadata_name_moved_narration is not None and metadata_name_moved_narration in relevant_posting.meta:
            moved_narration = relevant_posting.meta[metadata_name_moved_narration]
        if stayed_narration is None: stayed_narration = entry.narration
        if moved_narration is None: moved_narration = entry.narration
        return stayed_narration, moved_narration, metadata_name_moved_narration

    @staticmethod
    def __create_transfer_posting(main_posting, transfer_account, with_main_posting):
        units = data.Amount(-main_posting.units.number if with_main_posting else main_posting.units.number,
                            main_posting.units.currency)
        return data.Posting(transfer_account, units, None, None, None, None)

    @staticmethod
    def __recreate_existing_txn(txn, postings, narration):
        return data.Transaction(txn.meta, txn.date, txn.flag, txn.payee, narration, txn.tags, txn.links,
                                postings)

    @staticmethod
    def __create_new_txn(txn, postings, date, narration):
        return data.Transaction(txn.meta, date, txn.flag, txn.payee, narration, txn.tags, txn.links, postings)
