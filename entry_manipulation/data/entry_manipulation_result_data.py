from typing import List

from beancount.core import data


class EntryManipulationResultData(object):
    def __init__(self, entries: List[data.Transaction], other_data: List[object] = None):
        self.entries = entries
        self.other_data = other_data
