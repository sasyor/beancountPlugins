from abc import abstractmethod
from itertools import chain
from typing import List, Optional

from beancount.core import data

from .posting_wrapper_factory_base import PostingWrapperFactoryBase
from ...data.entry_manipulation_result_data import EntryManipulationResultData
from ...entry_manipulator_base import EntryManipulatorBase
from ...utils.rounder import Rounder


class PostingConsolidatorSomethingBase(EntryManipulatorBase):
    def __init__(self, config) -> None:
        super().__init__(config)

        self._rounder = Rounder(config.get("roundings"))
        self._posting_wrapper_factory: Optional[PostingWrapperFactoryBase] = None

    def execute(self, entry: data.Transaction) -> EntryManipulationResultData:
        if self._posting_wrapper_factory is None:
            return EntryManipulationResultData[entry]

        source_postings, target_postings, simple_postings, irrelevant_postings = self._posting_wrapper_factory.wrap_postings(
            entry.postings)

        postings: List[data.Posting] = []
        postings.extend(irrelevant_postings)
        for source_posting in source_postings:
            source_posting.process_postings(target_postings, simple_postings)
        for posting in chain(simple_postings, target_postings):
            postings.extend(posting.get_postings())

        new_entry = data.Transaction(entry.meta, entry.date, entry.flag, entry.payee, entry.narration, entry.tags,
                                     entry.links, postings)

        return EntryManipulationResultData([new_entry], self.get_other_data())

    @abstractmethod
    def get_other_data(self) -> Optional[List[object]]:
        pass
