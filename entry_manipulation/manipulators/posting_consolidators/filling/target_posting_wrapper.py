from decimal import Decimal
from typing import List

from beancount.core import data

from .can_add_posting import CanAddPosting
from .simple_posting_wrapper import SimplePostingWrapper
from ..ids import Ids
from ..target_posting_wrapper_base import TargetPostingWrapperBase


class TargetPostingWrapper(TargetPostingWrapperBase, CanAddPosting):
    def __init__(self, posting: data.Posting, ids: Ids):
        super().__init__(posting, ids)
        self._ids = ids
        self._simple_posting_wrapper = SimplePostingWrapper(posting)

    def get_ids(self) -> Ids:
        return self._ids

    def get_postings(self) -> List[data.Posting]:
        return self._simple_posting_wrapper.get_postings()

    def add_number(self, number: Decimal) -> None:
        return self._simple_posting_wrapper.add_number(number)
