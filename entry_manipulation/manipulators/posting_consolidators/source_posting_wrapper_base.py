from abc import abstractmethod
from decimal import Decimal
from typing import List

from beancount import Amount
from beancount.core import data

from .ids import Ids
from .simple_posting_wrapper_base import SimplePostingWrapperBase
from .target_posting_wrapper_base import TargetPostingWrapperBase
from ...utils.rounder import Rounder


class SourcePostingWrapperBase:
    def __init__(self, rounder: Rounder, posting: data.Posting, distribution_type: str, ids: Ids,
                 max_number: Decimal) -> None:
        self._rounder = rounder
        self._posting = posting
        self._distribution_type = distribution_type
        self._ids = ids
        self._max_number = max_number

    def process_postings(self, target_postings: List[TargetPostingWrapperBase],
                         simple_postings: List[SimplePostingWrapperBase]) -> None:
        postings: List[SimplePostingWrapperBase] = []
        for posting in target_postings:
            if posting.get_ids().is_ids_intersect(self._ids):
                postings.append(posting)

        if self._ids.is_intersect_with_simple_postings():
            for posting in simple_postings:
                postings.append(posting)

        number_base = 0
        if self._distribution_type == "unit":
            for posting in postings:
                number_base += posting.get_number()
            number_base = self._max_number / number_base
        elif self._distribution_type == "equal":
            number_base = self._max_number / len(postings)
        elif self._distribution_type.startswith("meta:"):
            for posting in postings:
                meta = posting.get_meta(self._distribution_type.split("meta:")[-1])
                if isinstance(meta, Amount):
                    number_base += meta.number
            number_base = self._max_number / number_base

        for posting in postings:
            number = 0
            if self._distribution_type == "unit":
                number = number_base * posting.get_number()
            elif self._distribution_type == "equal":
                number = number_base
            elif self._distribution_type.startswith("meta:"):
                meta = posting.get_meta(self._distribution_type.split("meta:")[-1])
                if isinstance(meta, Amount):
                    number = number_base * meta.number

            number = self._rounder.round(number, self._posting.units.currency)
            self.process_posting(posting, number)

    @abstractmethod
    def process_posting(self, posting: SimplePostingWrapperBase, number: Decimal) -> None:
        pass
