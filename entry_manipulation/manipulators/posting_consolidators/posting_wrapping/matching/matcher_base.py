from abc import ABC, abstractmethod
from typing import List


class MatcherBase(ABC):
    def __init__(self, match_data: List[str]):
        self._match_data = match_data

    @abstractmethod
    def is_matches(self, other_match_data: List[str]) -> bool:
        pass
