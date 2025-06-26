from decimal import Decimal
from typing import List, Dict, Optional

from beancount.core import data

from .target_posting_wrapper import TargetPostingWrapper
from ....data.account_consolidation_data_manager import AccountConsolidationDataManager


class TargetPostingBasicWrapper(TargetPostingWrapper):
    def __init__(self, account_consolidation_manager: AccountConsolidationDataManager, posting: data.Posting,
                 match_data: Optional[List[str]]):
        super().__init__(account_consolidation_manager, posting, match_data)

        self._numbers: Dict[data.Account, Decimal] = {}

    def get_postings(self) -> List[data.Posting]:
        postings: List[data.Posting] = [self.posting]
        for account_post_fix in self._numbers:
            number = self._numbers.get(account_post_fix)
            account = self.posting.account + ":" + account_post_fix
            postings.append(data.Posting(account,
                                         data.Amount(number, self.posting.units.currency), None,
                                         None, self.posting.flag, self.posting.meta))
            self._account_consolidation.add_additional_accounts({account})
        return postings
