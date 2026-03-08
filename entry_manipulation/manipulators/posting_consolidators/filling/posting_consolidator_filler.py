from typing import Optional, List

from .posting_wrapper_factory import PostingWrapperFactory
from ..posting_consolidator_something_base import PostingConsolidatorSomethingBase
from ..posting_wrapping.matching.id_matcher_factory import IdMatcherFactory
from ..posting_wrapping.values.metadata_value_getter import MetadataValueGetter
from ..posting_wrapping.values.value_getter import ValueGetter
from ....data.account_consolidation_data_manager import AccountConsolidationDataManager


class PostingConsolidatorFiller(PostingConsolidatorSomethingBase):
    def __init__(self, config):
        super().__init__(config)

        self._account_consolidation_manager = AccountConsolidationDataManager()

        metadata_name_distribution_type = config.get('metadata-name-fill-base')
        value_getter_distribution_type: ValueGetter = MetadataValueGetter(metadata_name_distribution_type)

        metadata_name_source_id = config.get('metadata-name-fill-source-id')
        metadata_name_target_id = config.get('metadata-name-fill-target-id')
        matcher_factory = IdMatcherFactory(metadata_name_source_id, metadata_name_target_id)

        self._posting_wrapper_factory = PostingWrapperFactory(self._rounder, value_getter_distribution_type,
                                                              matcher_factory)

    def get_other_data(self) -> Optional[List[object]]:
        return []
