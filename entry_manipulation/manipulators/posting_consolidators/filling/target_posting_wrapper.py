from decimal import Decimal
from typing import List, Dict, Optional

from beancount.core import data

from ..posting_wrapping.target_posting_wrapper_base import TargetPostingWrapperBase


class TargetPostingWrapper(TargetPostingWrapperBase):
    def __init__(self, posting: data.Posting, match_data: Optional[List[str]]):
        super().__init__(posting, match_data)
        self._numbers: Dict[data.Account, Decimal] = {}
        self._number: Decimal = Decimal(0)

    def get_postings(self) -> List[data.Posting]:
        new_posting = data.Posting(self.posting.account,
                                   data.Amount(self._number, self.posting.units.currency), self.posting.cost,
                                   self.posting.price, self.posting.flag, self.posting.meta)
        return [new_posting]

    def add_number(self, number: Decimal) -> None:
        self._number += number

    def get_number(self) -> Decimal:
        return self.posting.units.number

    def get_meta(self, meta_name: str) -> Optional[str]:
        return self.posting.meta.get(meta_name)
