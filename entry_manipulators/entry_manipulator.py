from abc import abstractmethod

from beancount.core import data

from entry_manipulators.data.entry_manipulation_result_data import EntryManipulationResultData


class EntryManipulator:
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def execute(self, entry: data.Transaction) -> EntryManipulationResultData:
        pass
