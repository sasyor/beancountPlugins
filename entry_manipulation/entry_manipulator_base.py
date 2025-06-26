from abc import abstractmethod, ABC

from beancount.core import data

from .data.entry_manipulation_result_data import EntryManipulationResultData


class EntryManipulatorBase(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def execute(self, entry: data.Transaction) -> EntryManipulationResultData:
        pass
