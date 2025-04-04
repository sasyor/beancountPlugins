from typing import Dict, Set

from beancount.core import data

from ..data.account_consolidation_data import AccountConsolidationData
from ..data.entry_manipulation_result_data import EntryManipulationResultData
from ..entry_manipulator_base import EntryManipulatorBase


class PostingConsolidator(EntryManipulatorBase):
    def __init__(self, config):
        super().__init__(config)

        self.consolidate_account_postfix = config.get('consolidate-account-postfix')
        self.metadata_name_consolidate_account_postfix = config.get('metadata-name-consolidate-account-postfix')

    def execute(self, entry: data.Transaction) -> EntryManipulationResultData:

        account_consolidators = self.get_account_consolidators(entry)

        new_postings = []
        for posting in entry.postings:
            new_posting = self.get_posting(posting, account_consolidators)
            new_postings.append(new_posting)

        new_transaction = data.Transaction(entry.meta, entry.date, entry.flag, entry.payee, entry.narration, entry.tags,
                                           entry.links, new_postings)

        return EntryManipulationResultData([new_transaction], list(account_consolidators.values()))

    def get_account_consolidators(self, entry):
        relevant_accounts = self.__get_relevant_accounts(entry.postings)
        account_consolidators: Dict[str, AccountConsolidationData] = {}
        for account in relevant_accounts:
            account_consolidators[account] = AccountConsolidationData(account,
                                                                      account + ':' + self.consolidate_account_postfix)
        return account_consolidators

    def get_posting(self, posting, account_consolidators):
        if self.metadata_name_consolidate_account_postfix in posting.meta:
            account = posting.account + ':' + posting.meta[self.metadata_name_consolidate_account_postfix]
            account_consolidators[posting.account].add_additional_accounts({account})
            new_posting = data.Posting(account, posting.units, posting.cost, posting.price, posting.flag,
                                       posting.meta)
            return new_posting
        elif posting.account in account_consolidators:
            account = account_consolidators[posting.account].to_account
            new_posting = data.Posting(account, posting.units, posting.cost, posting.price, posting.flag,
                                       posting.meta)
            return new_posting
        else:
            return posting

    def __get_relevant_accounts(self, postings):
        relevant_accounts: Set[str] = set()
        for posting in postings:
            if self.metadata_name_consolidate_account_postfix in posting.meta:
                relevant_accounts.add(posting.account)

        return relevant_accounts
