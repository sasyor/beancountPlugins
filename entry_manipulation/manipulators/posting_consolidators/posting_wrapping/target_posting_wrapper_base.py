from abc import abstractmethod, ABC
from decimal import Decimal
from typing import List, Optional, Dict

from beancount.core import data


class TargetPostingWrapperBase(ABC):
    def __init__(self, posting: data.Posting, match_data: Optional[List[str]]):
        self.posting = posting
        self._numbers: Dict[data.Account, Decimal] = {}
        self._match_data = match_data

    def get_match_data(self) -> Optional[List[str]]:
        return self._match_data

    @abstractmethod
    def get_postings(self) -> List[data.Posting]:
        pass

    def get_number(self) -> Decimal:
        return self.posting.units.number

    def get_meta(self, meta_name: str) -> Optional[str]:
        return self.posting.meta.get(meta_name)
