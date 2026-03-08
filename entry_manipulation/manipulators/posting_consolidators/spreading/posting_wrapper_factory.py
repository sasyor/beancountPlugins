from typing import List

from beancount.core import data

from .source_posting_wrapper import SourcePostingWrapper
from .target_posting_basic_wrapper import TargetPostingBasicWrapper
from .target_posting_with_cost_wrapper import TargetPostingWithCostWrapper
from ..posting_wrapping.account_naming.account_namers import AccountNamers
from ..posting_wrapping.matching.matcher_base import MatcherBase
from ..posting_wrapping.matching.matcher_factory_base import MatcherFactoryBase
from ..posting_wrapping.posting_wrapper_factory_base import PostingWrapperFactoryBase
from ..posting_wrapping.source_posting_wrapper_base import SourcePostingWrapperBase
from ..posting_wrapping.target_posting_wrapper_base import TargetPostingWrapperBase
from ..posting_wrapping.values.value_getter import ValueGetter
from ....data.account_consolidation_data_manager import AccountConsolidationDataManager
from ....utils.rounder import Rounder


class PostingWrapperFactory(PostingWrapperFactoryBase):
    def __init__(self, account_consolidation_manager: AccountConsolidationDataManager, rounder: Rounder,
                 value_getter_distribution_type: ValueGetter, matcher_factory: MatcherFactoryBase,
                 account_namers: AccountNamers):
        super().__init__(rounder, value_getter_distribution_type, matcher_factory)
        self._account_consolidation_manager = account_consolidation_manager
        self._account_namers = account_namers

    def _create_source_posting_wrapper(self, posting: data.Posting, distribution_type: str,
                                       matcher: MatcherBase) -> SourcePostingWrapperBase:
        return SourcePostingWrapper(self._rounder, posting, distribution_type, matcher, self._account_namers,
                                    posting.units.number)

    def _create_target_posting_wrapper(self, posting, match_data: List[str]) -> TargetPostingWrapperBase:
        if posting.cost is None:
            return TargetPostingBasicWrapper(self._account_consolidation_manager, posting, match_data)
        return TargetPostingWithCostWrapper(self._account_consolidation_manager, posting, match_data)
