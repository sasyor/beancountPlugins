from typing import List

from .matcher_base import MatcherBase


class IntersectMatcher(MatcherBase):
    def is_matches(self, other_match_data: List[str]) -> bool:
        if len(self._match_data) == 0: return True
        return len(set(self._match_data) & set(other_match_data)) != 0
