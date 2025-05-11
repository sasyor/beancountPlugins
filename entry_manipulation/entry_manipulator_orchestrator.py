import ast
from typing import Dict, List, Optional

from beancount.core import data

from .data.account_consolidation_data import AccountConsolidationData
from .data.entry_manipulation_result_data import EntryManipulationResultData
from .entry_manipulator_base import EntryManipulatorBase
from .manipulators.posting_consolidators.filling.posting_consolidator_filler import PostingConsolidatorFiller
from .manipulators.posting_consolidators.original_pricing.posting_consolidator_original_price import \
    PostingConsolidatorOriginalPrice
from .manipulators.posting_consolidators.spreading.posting_consolidator_spreader import PostingConsolidatorSpreader
from .manipulators.posting_splitter import PostingSplitter
from .manipulators.transaction_splitter import TransactionSplitter


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
        manipulators: List[EntryManipulatorBase] = []
        manipulator_factories = {
            "transaction-splitter": TransactionSplitter,
            "posting-consolidator-original-price": PostingConsolidatorOriginalPrice,
            "posting-spreader": PostingConsolidatorSpreader,
            "posting-filler": PostingConsolidatorFiller,
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
        other_data_collection: List[object] = []

        for entry in entries:
            if not isinstance(entry, data.Transaction):
                manipulated_entries.append(entry)
                continue

            current_entries_to_process = [entry]
            for manipulator in manipulators:
                next_entries_to_process = []
                for current_entry_to_process in current_entries_to_process:
                    result: Optional[EntryManipulationResultData]
                    try:
                        result = manipulator.execute(current_entry_to_process)
                    except Exception as e:
                        raise Exception(current_entry_to_process) from e
                    next_entries_to_process.extend(result.entries)
                    if result.other_data:
                        other_data_collection.extend(result.other_data)
                current_entries_to_process = next_entries_to_process

            manipulated_entries.extend(current_entries_to_process)

        for other_data in other_data_collection:
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
