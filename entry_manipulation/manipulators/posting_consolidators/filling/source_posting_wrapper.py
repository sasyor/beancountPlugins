from decimal import Decimal

from beancount.core import data

from .target_posting_wrapper import TargetPostingWrapper
from ..posting_wrapping.source_posting_wrapper_base import SourcePostingWrapperBase
from ..posting_wrapping.matching.matcher_base import MatcherBase
from ....utils.rounder import Rounder


class SourcePostingWrapper(SourcePostingWrapperBase):

    def __init__(self, rounder: Rounder, posting: data.Posting, distribution_type: str, matcher: MatcherBase,
                 max_number: Decimal):
        super().__init__(rounder, posting, distribution_type, matcher, max_number)

    def process_posting(self, posting: TargetPostingWrapper, number: Decimal) -> None:
        posting.add_number(number)
