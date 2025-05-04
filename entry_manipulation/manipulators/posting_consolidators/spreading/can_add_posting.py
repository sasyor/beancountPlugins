from abc import abstractmethod
from decimal import Decimal


class CanAddPosting:
    @abstractmethod
    def add_posting(self, account_post_fix: str, number: Decimal) -> None:
        pass
