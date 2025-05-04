from typing import List, Optional

from .posting_wrapper_factory import PostingWrapperFactory
from ..posting_consolidator_something_base import PostingConsolidatorSomethingBase
from ....data.account_consolidation_data_manager import AccountConsolidationDataManager


class PostingConsolidatorSpreader(PostingConsolidatorSomethingBase):
    def __init__(self, config):
        super().__init__(config)
        self._account_consolidation_manager = AccountConsolidationDataManager()
        metadata_name_spread_base = config.get('metadata-name-spread-base')
        metadata_name_source_id = config.get('metadata-name-spread-source-id')
        metadata_name_target_id = config.get('metadata-name-spread-target-id')
        account_postfix = config.get('consolidate-price-account-postfix')
        self._posting_wrapper_factory = PostingWrapperFactory(
            self._account_consolidation_manager, self._rounder, metadata_name_spread_base,
            metadata_name_source_id,
            metadata_name_target_id, account_postfix)

    def get_other_data(self) -> Optional[List[object]]:
        return self._account_consolidation_manager.get_account_consolidators()
