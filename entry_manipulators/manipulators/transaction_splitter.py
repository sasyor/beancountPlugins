import copy

from beancount.core import data

from entry_manipulators.entry_manipulator import EntryManipulator


class TransactionSplitter(EntryManipulator):
    def __init__(self, config):
        self.config = config

    def execute(self, entry):
        return self.__try_create_txn(self.config, entry)

    def __try_create_txn(self, rule, txn):
        metadata_name_date = rule["metadata-name-date"]
        metadata_names_to_remove = {metadata_name_date}

        relevant_postings_filters = [lambda posting: posting.meta and metadata_name_date in posting.meta]
        if "metadata-name-transfer-account" in rule:
            metadata_name_transfer_account = rule["metadata-name-transfer-account"]
            relevant_postings_filters.append(lambda posting: metadata_name_transfer_account in posting.meta)
            transfer_account_get = lambda posting: posting.meta[
                metadata_name_transfer_account
            ]
            metadata_names_to_remove.add(metadata_name_transfer_account)
        elif "transfer-account" in rule:
            if "account" in rule:
                relevant_postings_filters.append(lambda posting: posting.account == rule["account"])
            transfer_account_get = lambda posting: rule["transfer-account"]
        else:
            return [txn]

        relevant_postings = list(
            filter(
                lambda posting: all(f(posting) for f in relevant_postings_filters),
                txn.postings,
            )
        )
        if len(relevant_postings) == 0:
            return [txn]

        new_txns = []
        date = txn.date
        inverted_date_mode = rule.get("inverted-date-mode")
        if inverted_date_mode is True and len(relevant_postings) == 1:
            txn = txn._replace(date=self.__get_date(relevant_postings[0], metadata_name_date))

        for relevant_posting in relevant_postings:
            extra_metadata_names_to_remove = {}
            transfer_account = transfer_account_get(relevant_posting)

            if not inverted_date_mode:
                date = self.__get_date(relevant_posting, metadata_name_date)
            (narration, metadata_name_to_remove) = self.__get_narration(txn, relevant_posting, rule)

            if metadata_name_to_remove:
                extra_metadata_names_to_remove = {metadata_name_to_remove}

            self.__modify_existing_txn(txn, relevant_posting, transfer_account,
                                       metadata_names_to_remove.union(extra_metadata_names_to_remove))
            new_txns.append(self.__create_new_txn(
                txn,
                relevant_posting,
                date,
                narration,
                transfer_account,
            ))

        new_txns.append(txn)
        return new_txns

    @staticmethod
    def __get_date(relevant_posting, metadata_name_date):
        return relevant_posting.meta[metadata_name_date]

    @staticmethod
    def __get_narration(entry, relevant_posting, rule):
        metadata_name_narration = rule.get("metadata-name-narration")
        if metadata_name_narration is not None and metadata_name_narration in relevant_posting.meta:
            return relevant_posting.meta[metadata_name_narration], metadata_name_narration
        narration = rule.get("narration")
        if narration is not None:
            return narration, None
        return entry.narration, None

    @staticmethod
    def __modify_existing_txn(txn, relevant_posting, transfer_account, metadata_names_to_remove):
        for metadata_name_to_remove in metadata_names_to_remove:
            del relevant_posting.meta[metadata_name_to_remove]

        txn.postings.remove(relevant_posting)
        data.create_simple_posting(
            txn,
            transfer_account,
            relevant_posting.units.number,
            relevant_posting.units.currency,
        )

    @staticmethod
    def __create_new_txn(txn, relevant_posting, date, narration, transfer_account):
        # create new txn
        new_txn = copy.deepcopy(txn)
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
