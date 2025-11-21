from abc import abstractmethod, ABC
from typing import Optional, List

from beancount.core import data

from .matcher_base import MatcherBase


class MatcherFactoryBase(ABC):
    @abstractmethod
    def create_matcher(self, posting: data.Posting) -> Optional[MatcherBase]:
        pass

    @abstractmethod
    def create_match_data(self, posting: data.Posting) -> List[str]:
        pass
