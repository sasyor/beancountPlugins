from typing import Dict, List

from beancount.core import data

from .account_consolidation_data import AccountConsolidationData


class AccountConsolidationDataManager:
    def __init__(self):
        self._account_consolidators: Dict[data.Account, AccountConsolidationData] = {}

    def get_account_consolidators(self) -> List[AccountConsolidationData]:
        return list(self._account_consolidators.values())

    def add_new_consolidator(self, from_account: data.Account, to_account: data.Account) -> AccountConsolidationData:
        data = AccountConsolidationData(from_account, to_account)
        self._account_consolidators[to_account] = data
        return data

    def add_additional_accounts(self, from_account: data.Account, additional_account: data.Account):
        account_consolidator = self._account_consolidators.get(from_account)
        if account_consolidator is not None:
            account_consolidator.add_additional_accounts({additional_account})
