from abc import abstractmethod
from decimal import Decimal


class CanAddPosting:
    @abstractmethod
    def add_number(self, number: Decimal) -> None:
        pass
