from _decimal import Decimal
from typing import List

from beancount.core import data

from .can_add_posting import CanAddPosting
from ..simple_posting_wrapper_base import SimplePostingWrapperBase


class SimplePostingWrapper(SimplePostingWrapperBase, CanAddPosting):
    def __init__(self, posting: data.Posting):
        super().__init__(posting)
        self._number: Decimal = Decimal(0)

    def add_number(self, number: Decimal) -> None:
        self._number += number

    def get_postings(self) -> List[data.Posting]:
        new_posting = data.Posting(self._posting.account,
                                   data.Amount(self._number, self._posting.units.currency), self._posting.cost,
                                   self._posting.price, self._posting.flag, self._posting.meta)
        return [new_posting]
