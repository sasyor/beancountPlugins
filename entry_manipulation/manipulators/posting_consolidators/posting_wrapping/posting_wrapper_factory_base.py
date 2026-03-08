from abc import abstractmethod, ABC
from typing import List, Tuple

from beancount.core import data

from .matching.matcher_base import MatcherBase
from .matching.matcher_factory_base import MatcherFactoryBase
from .source_posting_wrapper_base import SourcePostingWrapperBase
from .target_posting_wrapper_base import TargetPostingWrapperBase
from .values.value_getter import ValueGetter
from ....utils.rounder import Rounder


class PostingWrapperFactoryBase(ABC):
    def __init__(self, rounder: Rounder, value_getter_distribution_type: ValueGetter,
                 matcher_factory: MatcherFactoryBase):
        self._rounder = rounder
        self.value_getter_distribution_type = value_getter_distribution_type
        self._matcher_factory = matcher_factory

    def wrap_postings(self, postings: List[data.Posting]) -> Tuple[List[SourcePostingWrapperBase],
    List[TargetPostingWrapperBase], List[data.Posting]]:
        source_postings: List[SourcePostingWrapperBase] = []
        target_postings: List[TargetPostingWrapperBase] = []
        irrelevant_postings: List[data.Posting] = []

        for posting in postings:
            source_matcher = self._matcher_factory.create_matcher(posting)
            if source_matcher is not None:
                distribution_type = self.value_getter_distribution_type.get_value(posting)

                source_postings.append(
                    self._create_source_posting_wrapper(posting, distribution_type, source_matcher))
            elif posting.account.startswith("Expenses:"):
                match_data = self._matcher_factory.create_match_data(posting)
                target_postings.append(self._create_target_posting_wrapper(posting, match_data))
            else:
                irrelevant_postings.append(posting)

        return source_postings, target_postings, irrelevant_postings

    @abstractmethod
    def _create_source_posting_wrapper(self, posting: data.Posting, distribution_type: str,
                                       matcher: MatcherBase) -> SourcePostingWrapperBase:
        pass

    @abstractmethod
    def _create_target_posting_wrapper(self, posting, match_data: List[str]) -> TargetPostingWrapperBase:
        pass
