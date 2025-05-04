from typing import Optional, List

from .posting_wrapper_factory import PostingWrapperFactory
from ..posting_consolidator_something_base import PostingConsolidatorSomethingBase
from ....data.account_consolidation_data_manager import AccountConsolidationDataManager


class PostingConsolidatorFiller(PostingConsolidatorSomethingBase):
    def __init__(self, config):
        super().__init__(config)
        self._account_consolidation_manager = AccountConsolidationDataManager()
        metadata_name_distribution_type = config.get('metadata-name-fill-base')
        metadata_name_source_id = config.get('metadata-name-fill-source-id')
        metadata_name_target_id = config.get('metadata-name-fill-target-id')
        self._posting_wrapper_factory = PostingWrapperFactory(
            self._account_consolidation_manager, self._rounder, metadata_name_distribution_type,
            metadata_name_source_id,
            metadata_name_target_id)

    def get_other_data(self) -> Optional[List[object]]:
        return []
