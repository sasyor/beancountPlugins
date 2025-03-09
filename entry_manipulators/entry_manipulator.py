from abc import abstractmethod
from typing import List

from beancount.core import data


class EntryManipulator:
    @abstractmethod
    def execute(self, entry: data.Transaction) -> List[data.Transaction]:
        pass
