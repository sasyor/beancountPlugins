from abc import abstractmethod, ABC
from decimal import Decimal
from typing import List

from beancount.core import data

from .matching.matcher_base import MatcherBase
from .target_posting_wrapper_base import TargetPostingWrapperBase
from ....utils.rounder import Rounder


# todo outsource distribution_type as distributor class
class SourcePostingWrapperBase(ABC):
    def __init__(self, rounder: Rounder, posting: data.Posting, distribution_type: str, matcher: MatcherBase,
                 max_number: Decimal) -> None:
        self._matcher = matcher
        self._rounder = rounder
        self._posting = posting
        self._distribution_type = distribution_type
        self._max_number = max_number

    def process_postings(self, target_postings: List[TargetPostingWrapperBase]) -> None:
        postings: List[TargetPostingWrapperBase] = []
        for posting in target_postings:
            if self._matcher.is_matches(posting.get_match_data()):
                postings.append(posting)

        if len(postings) == 0:
            return

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
                if isinstance(meta, data.Amount):
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
                if isinstance(meta, data.Amount):
                    number = number_base * meta.number

            number = self._rounder.round(number, self._posting.units.currency)
            self.process_posting(posting, number)

    @abstractmethod
    def process_posting(self, posting: TargetPostingWrapperBase, number: Decimal) -> None:
        pass
