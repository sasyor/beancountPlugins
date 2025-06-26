from abc import ABC
from decimal import Decimal
from typing import Optional, List

from beancount.core import data

from ....data.account_consolidation_data import AccountConsolidationData
from ....data.account_consolidation_data_manager import AccountConsolidationDataManager
from ..posting_wrapping.target_posting_wrapper_base import TargetPostingWrapperBase


class TargetPostingWrapper(TargetPostingWrapperBase, ABC):
    def __init__(self, account_consolidation_manager: AccountConsolidationDataManager, posting: data.Posting,
                 match_data: Optional[List[str]]):
        super().__init__(posting, match_data)

        self._account_consolidation_manager = account_consolidation_manager
        self._account_consolidation: Optional[AccountConsolidationData] = None

    def add_posting(self, source_account_postfix: str, target_account_postfix: str, number: Decimal) -> None:
        number_in_dict = self._numbers.get(source_account_postfix)
        if number_in_dict is None:
            self._numbers[source_account_postfix] = number
            self._account_consolidation = self._account_consolidation_manager.add_new_consolidator(
                self.posting.account,
                self.posting.account + ":" + target_account_postfix)
        else:
            self._numbers[source_account_postfix] += number

    def get_number(self) -> Decimal:
        return self.posting.units.number

    def get_meta(self, meta_name: str) -> Optional[str]:
        return self.posting.meta.get(meta_name)
