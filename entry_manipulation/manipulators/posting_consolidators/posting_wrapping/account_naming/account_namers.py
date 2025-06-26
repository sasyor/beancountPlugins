from .account_namer_base import AccountNamerBase


class AccountNamers:
    def __init__(self, source: AccountNamerBase, target: AccountNamerBase) -> None:
        self.source = source
        self.target = target
