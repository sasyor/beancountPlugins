from typing import Set


class AccountConsolidationData(object):
    def __init__(self, from_account: str, to_account: str, additional_accounts: Set[str] = None):
        self.original_account = from_account
        self.to_account = to_account
        if additional_accounts is None:
            additional_accounts = set()
        self.additional_accounts = additional_accounts

    def add_additional_accounts(self, additional_accounts: Set[str]):
        self.additional_accounts.update(additional_accounts)
