from typing import Set, Dict, List

from beancount.core import data

from .posting_consolidator_extracting_base import PostingConsolidatorExtractingBase
from ....data.account_consolidation_data import AccountConsolidationData


class PostingConsolidatorDiscounter(PostingConsolidatorExtractingBase):
    def __init__(self, config):
        super().__init__(config)
        self.consolidate_discount_account_postfix = config.get('consolidate-discount-account-postfix')
        self.metadata_name_discount = config.get('metadata-name-discount')

    def get_relevant_accounts(self, entry: data.Transaction) -> Set[str]:
        relevant_accounts: Set[str] = set()
        for posting in entry.postings:
            if posting.meta and self.metadata_name_discount in posting.meta:
                relevant_accounts.add(posting.account)

        return relevant_accounts

    def get_postings_from_posting(self, posting: data.Posting,
                                  account_consolidators: Dict[str, AccountConsolidationData]) -> List[
        data.Posting]:
        if not posting.meta or not self.metadata_name_discount in posting.meta:
            return [posting]

        discount_amount = posting.meta[self.metadata_name_discount]
        posting.meta.pop(self.metadata_name_discount)

        price_posting = data.Posting(posting.account, discount_amount, None, None, None, None)

        discount_account = posting.account + ':' + self.consolidate_discount_account_postfix
        discount_posting = data.Posting(discount_account, -discount_amount, None, None, None, None)

        account_consolidators[posting.account].add_additional_accounts({discount_account})

        return [posting, price_posting, discount_posting]
