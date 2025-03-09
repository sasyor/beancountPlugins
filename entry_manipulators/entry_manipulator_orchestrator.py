import ast
from typing import List

from beancount.core import data

from entry_manipulators.entry_manipulator import EntryManipulator
from entry_manipulators.manipulators.transaction_splitter import TransactionSplitter


class EntryManipulatorOrchestrator:

    def execute(self, entries, options_map, config_str=""):
        config = {}
        expr = ast.literal_eval(config_str)
        config.update(expr)

        manipulators: List[EntryManipulator] = []
        for manipulator in config["manipulators"]:
            if manipulator["type"] == "transaction-splitter":
                manipulators.append(TransactionSplitter(manipulator))
            else:
                raise Exception("Manipulator type not implemented: " + manipulator["type"])

        new_entries = []
        for entry in entries:
            if not isinstance(entry, data.Transaction):
                new_entries.append(entry)
                continue

            for manipulator in manipulators:
                for new_entry in manipulator.execute(entry):
                    new_entries.append(new_entry)

        return new_entries, []


entry_manipulator_obj = EntryManipulatorOrchestrator()


def entry_manipulator(entries, options_map, config_str=""):
    return entry_manipulator_obj.execute(entries, options_map, config_str)
