from beancount.core import data

from .account_namer_base import AccountNamerBase


class FixAccountNamer(AccountNamerBase):
    def __init__(self, postfix: str) -> None:
        self._postfix = postfix

    def get_account_name(self, source_posting: data.Posting, target_posting: data.Posting):
        return self._postfix
