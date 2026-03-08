from beancount.core import data

from .account_namer_base import AccountNamerBase


class MetadataAccountNamer(AccountNamerBase):
    def __init__(self, is_source_used: bool, metadata_name: str):
        self._is_source_used = is_source_used
        self._metadata_name = metadata_name

    def get_account_name(self, source_posting: data.Posting, target_posting: data.Posting):
        source_postfix = source_posting.meta.get(self._metadata_name) if source_posting.meta else None
        target_postfix = target_posting.meta.get(self._metadata_name) if target_posting.meta else None

        return source_postfix if self._is_source_used else target_postfix
