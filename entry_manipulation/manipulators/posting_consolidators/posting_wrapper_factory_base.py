from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Optional

from beancount.core import data

from .ids import Ids
from .simple_posting_wrapper_base import SimplePostingWrapperBase
from .source_posting_wrapper_base import SourcePostingWrapperBase
from .target_posting_wrapper_base import TargetPostingWrapperBase
from ...utils.rounder import Rounder


class PostingWrapperFactoryBase(metaclass=ABCMeta):
    def __init__(self, rounder: Rounder, metadata_name_distribution_type: str, metadata_name_source_id: str,
                 metadata_name_target_id: str):
        self._rounder = rounder
        self._metadata_name_distribution_type = metadata_name_distribution_type
        self._metadata_name_source_id = metadata_name_source_id
        self._metadata_name_target_id = metadata_name_target_id

    def wrap_postings(self, postings: List[data.Posting]) -> Tuple[List[SourcePostingWrapperBase],
    List[TargetPostingWrapperBase], List[SimplePostingWrapperBase], List[data.Posting]]:
        source_postings: List[SourcePostingWrapperBase] = []
        target_postings: List[TargetPostingWrapperBase] = []
        simple_postings: List[SimplePostingWrapperBase] = []
        irrelevant_postings: List[data.Posting] = []

        for posting in postings:
            source_id_text: Optional[str] = posting.meta.get(self._metadata_name_source_id)
            target_id_text: Optional[str] = posting.meta.get(self._metadata_name_target_id)
            if source_id_text is not None:
                distribution_type = posting.meta.get(self._metadata_name_distribution_type)
                source_postings.append(self._create_source_posting_wrapper(posting, distribution_type, source_id_text))
            elif target_id_text is not None:
                target_postings.append(self._create_target_posting_wrapper(posting, target_id_text))
            elif posting.account.startswith("Expenses:"):
                simple_postings.append(self._create_simple_posting_wrapper(posting))
            else:
                irrelevant_postings.append(posting)

        return source_postings, target_postings, simple_postings, irrelevant_postings

    @abstractmethod
    def _create_source_posting_wrapper(self, posting: data.Posting, distribution_type: str,
                                       ids_text: str) -> SourcePostingWrapperBase:
        pass

    @abstractmethod
    def _create_simple_posting_wrapper(self, posting) -> SimplePostingWrapperBase:
        pass

    @abstractmethod
    def _create_target_posting_wrapper(self, posting, ids_text: str) -> TargetPostingWrapperBase:
        pass

    @staticmethod
    def _create_ids(ids_text: str) -> Ids:
        ids: List[int] = []
        if ids_text == "all":
            return Ids(ids)
        for id_text in ids_text.split(","):
            ids.append(int(id_text))
        return Ids(ids)
