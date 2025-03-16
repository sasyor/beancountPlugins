import ast
from typing import List, Dict

from beancount.core import data

from entry_manipulators.data.account_consolidation_data import AccountConsolidationData
from entry_manipulators.data.entry_manipulation_result_data import EntryManipulationResultData
from entry_manipulators.entry_manipulator import EntryManipulator
from entry_manipulators.manipulators.posting_consolidator import PostingConsolidator
from entry_manipulators.manipulators.posting_splitter import PostingSplitter
from entry_manipulators.manipulators.transaction_splitter import TransactionSplitter


class EntryManipulatorOrchestrator:
    def __init__(self):
        self.account_consolidators: Dict[str, AccountConsolidationData] = {}

    def execute(self, entries, options_map, config_str=""):
        config = {}
        expr = ast.literal_eval(config_str)
        config.update(expr)

        manipulators = self.get_manipulators(config)
        manipulated_entries = self.manipulate_entries(entries, manipulators)
        consolidated_entries = self.consolidate_entries(manipulated_entries)

        return consolidated_entries, []

    @staticmethod
    def get_manipulators(config):
        manipulators: List[EntryManipulator] = []
        manipulator_factories = {
            "transaction-splitter": TransactionSplitter,
            "posting-consolidator": PostingConsolidator,
            "posting-splitter": PostingSplitter,
        }
        for manipulator_config in config["manipulators"]:
            manipulator_factory = manipulator_factories.get(manipulator_config["type"])
            if manipulator_factory is not None:
                manipulators.append(manipulator_factory(manipulator_config))
            else:
                raise Exception("Manipulator type not implemented: " + manipulator_config["type"])
        return manipulators

    def manipulate_entries(self, entries, manipulators):
        manipulated_entries = []
        results: List[EntryManipulationResultData] = []
        for entry in entries:
            if not isinstance(entry, data.Transaction):
                manipulated_entries.append(entry)
                continue

            for manipulator in manipulators:
                results.append(manipulator.execute(entry))

        for result in results:
            manipulated_entries.extend(result.entries)

            if result.other_data is None:
                continue

            for other_data in result.other_data:
                if not isinstance(other_data, AccountConsolidationData):
                    continue

                account_consolidator = self.account_consolidators.get(other_data.original_account)
                if account_consolidator is None:
                    self.account_consolidators[other_data.original_account] = other_data
                else:
                    account_consolidator.add_additional_accounts(other_data.additional_accounts)

        return manipulated_entries

    def consolidate_entries(self, entries):
        consolidated_entries = []
        for entry in entries:
            if isinstance(entry, data.Open) and entry.account in self.account_consolidators:
                consolidated_entries.extend(self.consolidate_open(entry))
            elif isinstance(entry, data.Transaction):
                new_postings = []
                for posting in entry.postings:
                    account_consolidator = self.account_consolidators.get(posting.account)
                    if account_consolidator is None:
                        new_postings.append(posting)
                        continue
                    new_posting = data.Posting(account_consolidator.to_account, posting.units, posting.cost,
                                               posting.price, posting.flag, posting.meta)
                    new_postings.append(new_posting)
                consolidated_entry = data.Transaction(entry.meta, entry.date, entry.flag, entry.payee, entry.narration,
                                                      entry.tags, entry.links, new_postings)
                consolidated_entries.append(consolidated_entry)
            else:
                consolidated_entries.append(entry)
        return consolidated_entries

    def consolidate_open(self, entry):
        consolidated_entries = []
        account_consolidator = self.account_consolidators[entry.account]
        consolidated_entry = data.Open(entry.meta, entry.date, account_consolidator.to_account,
                                       entry.currencies, entry.booking)
        consolidated_entries.append(consolidated_entry)
        for additional_account in account_consolidator.additional_accounts:
            consolidated_entry = data.Open(entry.meta, entry.date, additional_account,
                                           entry.currencies, entry.booking)
            consolidated_entries.append(consolidated_entry)
        return consolidated_entries


def entry_manipulator(entries, options_map, config_str=""):
    return EntryManipulatorOrchestrator().execute(entries, options_map, config_str)
