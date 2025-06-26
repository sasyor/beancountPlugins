from abc import abstractmethod, ABC

from beancount.core import data


class AccountNamerBase(ABC):
    @abstractmethod
    def get_account_name(self, source_posting: data.Posting, target_posting: data.Posting):
        pass
