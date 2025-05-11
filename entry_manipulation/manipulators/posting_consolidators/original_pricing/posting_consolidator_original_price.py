from typing import Set, Dict, List

from beancount.core import data

from .posting_consolidator_original_price_base import PostingConsolidatorOriginalPriceBase
from ....data.account_consolidation_data import AccountConsolidationData


class PostingConsolidatorOriginalPrice(PostingConsolidatorOriginalPriceBase):
    def __init__(self, config):
        super().__init__(config)
        self.consolidate_discount_account_postfix = config.get('consolidate-discount-account-postfix')
        self.metadata_name_original_price = config.get('metadata-name-original-price')

    def get_relevant_accounts(self, entry: data.Transaction) -> Set[str]:
        relevant_accounts: Set[str] = set()
        for posting in entry.postings:
            if posting.meta and self.metadata_name_original_price in posting.meta:
                relevant_accounts.add(posting.account)

        return relevant_accounts

    def get_postings_from_posting(self, posting: data.Posting,
                                  account_consolidators: Dict[str, AccountConsolidationData]) -> List[
        data.Posting]:
        if posting.meta and self.metadata_name_original_price in posting.meta:
            price_units = posting.meta[self.metadata_name_original_price]
            posting.meta.pop(self.metadata_name_original_price)
            price_posting = data.Posting(posting.account, price_units, posting.cost, posting.price, posting.flag,
                                         posting.meta)

            discount_account = posting.account + ':' + self.consolidate_discount_account_postfix
            discount_units = data.Amount(posting.units.number - price_units.number, posting.units.currency)
            discount_posting = data.Posting(discount_account, discount_units, posting.cost, posting.price,
                                            posting.flag, None)
            account_consolidators[posting.account].add_additional_accounts({discount_account})

            return [price_posting, discount_posting]
        else:
            return [posting]
