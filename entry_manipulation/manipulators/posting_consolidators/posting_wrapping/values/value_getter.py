from abc import abstractmethod, ABC

from beancount.core import data


class ValueGetter(ABC):
    @abstractmethod
    def get_value(self, posting: data.Posting) -> str:
        pass
