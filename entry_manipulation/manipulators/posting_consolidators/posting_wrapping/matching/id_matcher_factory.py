from typing import Optional, List

from beancount.core import data

from .intersect_matcher import IntersectMatcher
from .matcher_base import MatcherBase
from .matcher_factory_base import MatcherFactoryBase


class IdMatcherFactory(MatcherFactoryBase):
    def __init__(self, metadata_name_source_id: str, metadata_name_target_id: Optional[str]):
        self._metadata_name_source_id = metadata_name_source_id
        self._metadata_name_target_id = metadata_name_target_id

    def create_matcher(self, posting: data.Posting) -> Optional[MatcherBase]:
        source_id_text: Optional[str] = posting.meta.get(self._metadata_name_source_id) if posting.meta else None
        return IntersectMatcher(self._create_ids(source_id_text)) if source_id_text else None

    def create_match_data(self, posting: data.Posting) -> List[str]:
        if not self._metadata_name_target_id: return []

        target_id_text: Optional[str] = posting.meta.get(self._metadata_name_target_id) if posting.meta else None
        if target_id_text:
            posting.meta.pop(self._metadata_name_target_id)
            return self._create_ids(target_id_text)

        return []

    @staticmethod
    def _create_ids(ids_text: str) -> List[str]:
        ids: List[str] = []
        if ids_text == "all":
            return ids
        for id_text in ids_text.split(","):
            ids.append(id_text)
        return ids
