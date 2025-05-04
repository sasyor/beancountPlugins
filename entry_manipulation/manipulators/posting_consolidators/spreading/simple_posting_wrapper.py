from _decimal import Decimal
from typing import Optional, List

from beancount.core import data

from .can_add_posting import CanAddPosting
from ..simple_posting_wrapper_base import SimplePostingWrapperBase
from ....data.account_consolidation_data import AccountConsolidationData
from ....data.account_consolidation_data_manager import AccountConsolidationDataManager


class SimplePostingWrapper(SimplePostingWrapperBase, CanAddPosting):
    def __init__(self, account_consolidation_manager: AccountConsolidationDataManager, account_postfix: str,
                 posting: data.Posting):
        super().__init__(posting)

        self._account_consolidation_manager = account_consolidation_manager
        self._account_postfix = account_postfix
        self._account_consolidation: Optional[AccountConsolidationData] = None

    def add_posting(self, account_post_fix: str, number: Decimal) -> None:
        number_in_dict = self._numbers.get(account_post_fix)
        if number_in_dict is None:
            self._numbers[account_post_fix] = number
            self._account_consolidation = self._account_consolidation_manager.add_new_consolidator(
                self._posting.account,
                self._posting.account + ":" + self._account_postfix)
        else:
            self._numbers[account_post_fix] += number

    def get_postings(self) -> List[data.Posting]:
        postings: List[data.Posting] = [self._posting]
        for account_post_fix in self._numbers:
            number_in_dict = self._numbers.get(account_post_fix)
            account = self._posting.account + ":" + account_post_fix
            postings.append(data.Posting(account,
                                         data.Amount(number_in_dict, self._posting.units.currency), self._posting.cost,
                                         self._posting.price, self._posting.flag, self._posting.meta))
            self._account_consolidation.add_additional_accounts({account})
        return postings
