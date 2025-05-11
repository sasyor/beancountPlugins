from abc import abstractmethod
from typing import List

from beancount.core import data

from .ids import Ids
from .simple_posting_wrapper_base import SimplePostingWrapperBase


class TargetPostingWrapperBase(SimplePostingWrapperBase):
    def __init__(self, posting: data.Posting, ids: Ids):
        super().__init__(posting)
        self._ids = ids

    def get_ids(self) -> Ids:
        return self._ids

    @abstractmethod
    def get_postings(self) -> List[data.Posting]:
        pass
