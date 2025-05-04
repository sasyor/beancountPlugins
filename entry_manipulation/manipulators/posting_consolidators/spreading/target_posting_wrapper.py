from decimal import Decimal
from typing import List

from beancount.core import data

from .can_add_posting import CanAddPosting
from .simple_posting_wrapper import SimplePostingWrapper
from ..ids import Ids
from ..target_posting_wrapper_base import TargetPostingWrapperBase
from ....data.account_consolidation_data_manager import AccountConsolidationDataManager


class TargetPostingWrapper(TargetPostingWrapperBase, CanAddPosting):
    def __init__(self, account_consolidation_manager: AccountConsolidationDataManager, account_postfix: str,
                 posting: data.Posting, ids: Ids):
        super().__init__(posting, ids)
        self._ids = ids
        self._simple_posting_wrapper = SimplePostingWrapper(account_consolidation_manager, account_postfix, posting)

    def get_ids(self) -> Ids:
        return self._ids

    def get_postings(self) -> List[data.Posting]:
        return self._simple_posting_wrapper.get_postings()

    def add_posting(self, account_post_fix: str, number: Decimal) -> None:
        return self._simple_posting_wrapper.add_posting(account_post_fix, number)
