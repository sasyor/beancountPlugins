from beancount.core import data

from .account_namer_base import AccountNamerBase


class ReuseLastPartAccountNamer(AccountNamerBase):
    def __init__(self, is_source_used):
        self._is_source_used = is_source_used

    def get_account_name(self, source_posting: data.Posting, target_posting: data.Posting):
        return source_posting.account.split(":")[-1] if self._is_source_used else target_posting.account.split(":")[-1]
