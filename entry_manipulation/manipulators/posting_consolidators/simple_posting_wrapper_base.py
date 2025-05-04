from abc import abstractmethod
from decimal import Decimal
from typing import Dict, List, Optional

from beancount.core import data


class SimplePostingWrapperBase:
    def __init__(self, posting: data.Posting):
        self._posting = posting
        self._numbers: Dict[data.Account, Decimal] = {}

    def get_number(self) -> Decimal:
        return self._posting.units.number

    def get_meta(self, meta_name: str) -> Optional[str]:
        return self._posting.meta.get(meta_name)

    @abstractmethod
    def get_postings(self) -> List[data.Posting]:
        pass
