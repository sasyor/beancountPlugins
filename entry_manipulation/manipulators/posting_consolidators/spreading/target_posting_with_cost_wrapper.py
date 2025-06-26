from typing import List, Optional

from beancount.core import data

from .target_posting_wrapper import TargetPostingWrapper
from ....data.account_consolidation_data_manager import AccountConsolidationDataManager


class TargetPostingWithCostWrapper(TargetPostingWrapper):
    def __init__(self, account_consolidation_manager: AccountConsolidationDataManager, posting: data.Posting,
                 match_data: Optional[List[str]]):
        super().__init__(account_consolidation_manager, posting, match_data)

    def get_postings(self) -> List[data.Posting]:
        postings: List[data.Posting] = []
        unit_number = self.posting.units.number * self.posting.cost.number

        for account_post_fix in self._numbers:
            number = self._numbers.get(account_post_fix)

            postings.append(self.create_cost_posting_supplementary_posting(account_post_fix, number))
            postings.append(self.create_cost_posting_opposition(number))

            unit_number = unit_number + number

        cost_number = unit_number / self.posting.units.number

        posting = self.create_cost_posting_modified(cost_number)
        postings.append(posting)

        return postings

    def create_cost_posting_modified(self, cost_number):
        cost = data.Cost(cost_number, self.posting.cost.currency, self.posting.cost.date, self.posting.cost.label)
        posting = data.Posting(self.posting.account, self.posting.units, cost, self.posting.price, self.posting.flag,
                               self.posting.meta)
        return posting

    def create_cost_posting_opposition(self, number):
        posting = data.Posting(self.posting.account, -data.Amount(number, self.posting.cost.currency),
                               None,
                               None, self.posting.flag, self.posting.meta)
        return posting

    def create_cost_posting_supplementary_posting(self, account_post_fix, number):
        account = self.posting.account + ":" + account_post_fix
        posting = data.Posting(account, data.Amount(number, self.posting.cost.currency), None,
                               None, self.posting.flag, self.posting.meta)
        self._account_consolidation.add_additional_accounts({account})
        return posting
