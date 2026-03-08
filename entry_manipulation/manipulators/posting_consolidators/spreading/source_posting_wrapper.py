from decimal import Decimal

from beancount.core import data

from .target_posting_with_cost_wrapper import TargetPostingWithCostWrapper
from ..posting_wrapping.account_naming.account_namers import AccountNamers
from ..posting_wrapping.source_posting_wrapper_base import SourcePostingWrapperBase
from ..posting_wrapping.matching.matcher_base import MatcherBase
from ....utils.rounder import Rounder


class SourcePostingWrapper(SourcePostingWrapperBase):

    def __init__(self, rounder: Rounder, posting: data.Posting, distribution_type: str, matcher: MatcherBase,
                 account_namers: AccountNamers,
                 max_number: Decimal):
        super().__init__(rounder, posting, distribution_type, matcher, max_number)
        self._account_namers = account_namers

    def process_posting(self, posting: TargetPostingWithCostWrapper, number: Decimal) -> None:
        source_account_postfix = self._account_namers.source.get_account_name(self._posting, posting.posting)
        target_account_postfix = self._account_namers.target.get_account_name(self._posting, posting.posting)
        posting.add_posting(source_account_postfix, target_account_postfix, number)
