from beancount.core import data

from .simple_posting_wrapper import SimplePostingWrapper
from .source_posting_wrapper import SourcePostingWrapper
from .target_posting_wrapper import TargetPostingWrapper
from ..posting_wrapper_factory_base import PostingWrapperFactoryBase
from ..simple_posting_wrapper_base import SimplePostingWrapperBase
from ..source_posting_wrapper_base import SourcePostingWrapperBase
from ..target_posting_wrapper_base import TargetPostingWrapperBase
from ....data.account_consolidation_data_manager import AccountConsolidationDataManager
from ....utils.rounder import Rounder


class PostingWrapperFactory(PostingWrapperFactoryBase):
    def __init__(self, account_consolidation_manager: AccountConsolidationDataManager, rounder: Rounder,
                 metadata_name_distribution_type: str, metadata_name_source_id: str, metadata_name_target_id: str,
                 account_postfix: str):
        super().__init__(rounder, metadata_name_distribution_type, metadata_name_source_id, metadata_name_target_id)
        self._account_consolidation_manager = account_consolidation_manager
        self._account_postfix = account_postfix

    def _create_source_posting_wrapper(self, posting: data.Posting, distribution_type: str,
                                       ids_text: str) -> SourcePostingWrapperBase:
        ids = self._create_ids(ids_text)
        account_post_fix = posting.account.split(":")[-1]
        max_number = posting.units.number
        return SourcePostingWrapper(self._rounder, posting, distribution_type, ids, account_post_fix, max_number)

    def _create_simple_posting_wrapper(self, posting) -> SimplePostingWrapperBase:
        return SimplePostingWrapper(self._account_consolidation_manager, self._account_postfix, posting)

    def _create_target_posting_wrapper(self, posting, ids_text: str) -> TargetPostingWrapperBase:
        posting.meta.pop(self._metadata_name_target_id)
        ids = self._create_ids(ids_text)
        return TargetPostingWrapper(self._account_consolidation_manager, self._account_postfix, posting, ids)
