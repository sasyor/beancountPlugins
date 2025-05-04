from decimal import Decimal

from beancount.core import data

from .simple_posting_wrapper import SimplePostingWrapper
from ..ids import Ids
from ..source_posting_wrapper_base import SourcePostingWrapperBase
from ....utils.rounder import Rounder


class SourcePostingWrapper(SourcePostingWrapperBase):

    def __init__(self, rounder: Rounder, posting: data.Posting, distribution_type: str, ids: Ids, account_post_fix: str,
                 max_number: Decimal):
        super().__init__(rounder, posting, distribution_type, ids, max_number)
        self._account_post_fix = account_post_fix

    def process_posting(self, posting: SimplePostingWrapper, number: Decimal) -> None:
        posting.add_posting(self._account_post_fix, number)
