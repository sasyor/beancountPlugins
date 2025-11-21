from typing import List

from beancount.core import data

from .source_posting_wrapper import SourcePostingWrapper
from .target_posting_wrapper import TargetPostingWrapper
from ..posting_wrapping.matching.matcher_base import MatcherBase
from ..posting_wrapping.matching.matcher_factory_base import MatcherFactoryBase
from ..posting_wrapping.posting_wrapper_factory_base import PostingWrapperFactoryBase
from ..posting_wrapping.source_posting_wrapper_base import SourcePostingWrapperBase
from ..posting_wrapping.target_posting_wrapper_base import TargetPostingWrapperBase
from ..posting_wrapping.values.value_getter import ValueGetter
from ....utils.rounder import Rounder


class PostingWrapperFactory(PostingWrapperFactoryBase):
    def __init__(self, rounder: Rounder, value_getter_distribution_type: ValueGetter,
                 matcher_factory: MatcherFactoryBase):
        super().__init__(rounder, value_getter_distribution_type, matcher_factory)

    def _create_source_posting_wrapper(self, posting: data.Posting, distribution_type: str,
                                       matcher: MatcherBase) -> SourcePostingWrapperBase:
        return SourcePostingWrapper(self._rounder, posting, distribution_type, matcher, posting.units.number)

    def _create_target_posting_wrapper(self, posting, match_data: List[str]) -> TargetPostingWrapperBase:
        return TargetPostingWrapper(posting, match_data)
