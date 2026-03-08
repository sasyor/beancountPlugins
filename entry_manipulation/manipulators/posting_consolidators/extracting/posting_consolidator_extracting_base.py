from abc import abstractmethod
from typing import Dict, Set, List

from beancount.core import data

from ....data.account_consolidation_data import AccountConsolidationData
from ....data.entry_manipulation_result_data import EntryManipulationResultData
from ....entry_manipulator_base import EntryManipulatorBase


class PostingConsolidatorExtractingBase(EntryManipulatorBase):
    def __init__(self, config):
        super().__init__(config)

        self.consolidate_price_account_postfix = config.get('consolidate-price-account-postfix')

    def execute(self, entry: data.Transaction) -> EntryManipulationResultData:
        account_consolidators = self.get_account_consolidators(entry)

        new_postings = self.get_postings(entry, account_consolidators)

        new_transaction = data.Transaction(entry.meta, entry.date, entry.flag, entry.payee, entry.narration, entry.tags,
                                           entry.links, new_postings)

        return EntryManipulationResultData([new_transaction], list(account_consolidators.values()))

    def get_account_consolidators(self, entry: data.Transaction) -> Dict[str, AccountConsolidationData]:
        relevant_accounts: Set[str] = set()
        relevant_accounts = relevant_accounts.union(self.get_relevant_accounts(entry))

        account_consolidators: Dict[str, AccountConsolidationData] = {}
        for account in relevant_accounts:
            account_consolidators[account] = AccountConsolidationData(account,
                                                                      account + ':' + self.consolidate_price_account_postfix)
        return account_consolidators

    @abstractmethod
    def get_relevant_accounts(self, entry: data.Transaction) -> Set[str]:
        pass

    def get_postings(self, entry: data.Transaction, account_consolidators: Dict[str, AccountConsolidationData]) -> List[
        data.Posting]:

        current_items = entry.postings
        next_items: List[data.Posting] = []
        for current_item in current_items:
            next_items.extend(self.get_postings_from_posting(current_item, account_consolidators))
        current_items = next_items

        return current_items

    @abstractmethod
    def get_postings_from_posting(self, posting: data.Posting,
                                  account_consolidators: Dict[str, AccountConsolidationData]) -> List[
        data.Posting]:
        pass
