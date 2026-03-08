from typing import Optional, List

from beancount.core import data

from .intersect_matcher import IntersectMatcher
from .matcher_base import MatcherBase
from .matcher_factory_base import MatcherFactoryBase


class AccountMatcherFactory(MatcherFactoryBase):
    def __init__(self, metadata_name_spread_account_postfix):
        self._metadata_name_spread_account_postfix = metadata_name_spread_account_postfix

    def create_matcher(self, posting: data.Posting) -> Optional[MatcherBase]:
        if posting.meta and self._metadata_name_spread_account_postfix in posting.meta:
            return IntersectMatcher([posting.account])
        else:
            return None

    def create_match_data(self, posting: data.Posting) -> List[str]:
        return [posting.account]
