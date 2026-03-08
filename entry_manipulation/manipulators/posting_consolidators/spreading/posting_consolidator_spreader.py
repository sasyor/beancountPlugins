from typing import List, Optional

from .posting_wrapper_factory import PostingWrapperFactory
from ..posting_consolidator_something_base import PostingConsolidatorSomethingBase
from ..posting_wrapping.account_naming.metadata_account_namer import MetadataAccountNamer
from ..posting_wrapping.account_naming.reuse_last_part_account_namer import ReuseLastPartAccountNamer
from ..posting_wrapping.account_naming.account_namers import AccountNamers
from ..posting_wrapping.account_naming.fix_account_namer import FixAccountNamer
from ..posting_wrapping.matching.account_matcher_factory import AccountMatcherFactory
from ..posting_wrapping.values.fixed_value_getter import FixedValueGetter
from ..posting_wrapping.values.metadata_value_getter import MetadataValueGetter
from ..posting_wrapping.values.value_getter import ValueGetter
from ..posting_wrapping.matching.id_matcher_factory import IdMatcherFactory
from ....data.account_consolidation_data_manager import AccountConsolidationDataManager


class PostingConsolidatorSpreader(PostingConsolidatorSomethingBase):
    def __init__(self, config):
        super().__init__(config)
        self._account_consolidation_manager = AccountConsolidationDataManager()

        value_getter_distribution_type: ValueGetter = FixedValueGetter(None)  # todo
        fix_spread_base = config.get('spread-base')
        if fix_spread_base is not None:
            value_getter_distribution_type: ValueGetter = FixedValueGetter(fix_spread_base)
        metadata_name_spread_base = config.get('metadata-name-spread-base')
        if metadata_name_spread_base is not None:
            value_getter_distribution_type: ValueGetter = MetadataValueGetter(metadata_name_spread_base)

        metadata_name_source_id: Optional[str] = config.get('metadata-name-spread-source-id')
        metadata_name_target_id: Optional[str] = config.get('metadata-name-spread-target-id')
        metadata_name_spread_account_postfix: Optional[str] = config.get('metadata-name-spread-account-postfix')
        if metadata_name_source_id:
            matcher_factory = IdMatcherFactory(metadata_name_source_id, metadata_name_target_id)
        elif config.get('match-mode') == 'same-account' and metadata_name_spread_account_postfix:
            matcher_factory = AccountMatcherFactory(metadata_name_spread_account_postfix)
        else:
            return

        account_postfix = config.get('consolidate-price-account-postfix')

        if metadata_name_spread_account_postfix:
            source_account_namer = MetadataAccountNamer(True, metadata_name_spread_account_postfix)
        else:
            source_account_namer = ReuseLastPartAccountNamer(True)
        target_account_namer = FixAccountNamer(account_postfix)
        account_namers = AccountNamers(source_account_namer, target_account_namer)

        self._posting_wrapper_factory = PostingWrapperFactory(
            self._account_consolidation_manager, self._rounder, value_getter_distribution_type,
            matcher_factory,
            account_namers)

    def get_other_data(self) -> Optional[List[object]]:
        return self._account_consolidation_manager.get_account_consolidators()
