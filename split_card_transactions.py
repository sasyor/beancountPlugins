import ast
import collections
import copy

from beancount.core import data

__plugins__ = ["split_card_transactions"]

SplitCardTransactionError = collections.namedtuple(
    "SplitCardTransactionError", "source message entry"
)


def split_card_transactions(entries, options_map, config_str=""):
    config = {
        "booking_date": "booking-date",
        "booking_transfer_account": "booking-transfer-account",
        "booking_posting_narration": "Card transaction booking",
        "account_based_splitters": [],
    }

    if config_str.strip():
        errors = []
        try:
            expr = ast.literal_eval(config_str)
            config.update(expr)
        except (SyntaxError, ValueError):
            errors.append(
                SplitCardTransactionError(
                    data.new_metadata(options_map["filename"], 0),
                    f"Syntax error in config: {config_str}",
                    None,
                )
            )
            return entries, errors

    meta_name_booking_date = config["booking_date"]
    meta_name_booking_transfer_account = config["booking_transfer_account"]
    booking_posting_narration = config["booking_posting_narration"]

    new_entries = []

    def split_booking_txn(original_posting_with_booking_date, transfer_account_config):
        booking_date = original_posting_with_booking_date.meta[meta_name_booking_date]
        booking_transfer_account = None
        if transfer_account_config["type"] == "account":
            booking_transfer_account = transfer_account_config["data"]
        elif transfer_account_config["type"] == "meta":
            booking_transfer_account = original_posting_with_booking_date.meta[
                transfer_account_config["data"]
            ]
        if booking_transfer_account is None:
            return None
        booking_unit_number = original_posting_with_booking_date.units.number
        booking_currency_number = original_posting_with_booking_date.units.currency
        del original_posting_with_booking_date.meta[meta_name_booking_date]
        if transfer_account_config["type"] == "meta":
            del original_posting_with_booking_date.meta[transfer_account_config["data"]]

        # booking entry: create
        booking_entry = copy.deepcopy(entry)
        booking_entry = booking_entry._replace(
            payee=None,
            narration=booking_posting_narration,
            date=booking_date,
            postings=[original_posting_with_booking_date],
        )
        data.create_simple_posting(
            booking_entry,
            booking_transfer_account,
            -booking_unit_number,
            booking_currency_number,
        )

        # existing entry: remove original posting with booking date
        entry.postings.remove(original_posting_with_booking_date)
        data.create_simple_posting(
            entry,
            booking_transfer_account,
            booking_unit_number,
            booking_currency_number,
        )

        return booking_entry

    def split_txn_metadata_based_splitter(entry):
        relevant_postings = list(
            filter(
                lambda posting: posting.meta
                and meta_name_booking_date in posting.meta
                and meta_name_booking_transfer_account in posting.meta,
                entry.postings,
            )
        )

        if len(relevant_postings) != 1:
            return None

        return split_booking_txn(
            relevant_postings[0],
            {"type": "meta", "data": meta_name_booking_transfer_account},
        )

    def split_txn_account_based_splitter(config, entry):
        account_based_splitters = config["account_based_splitters"]
        for account_based_splitter in account_based_splitters:
            relevant_postings = list(
                filter(
                    lambda posting: posting.meta
                    and meta_name_booking_date in posting.meta
                    and account_based_splitter["account"] == posting.account,
                    entry.postings,
                )
            )

            if len(relevant_postings) != 1:
                continue

            return split_booking_txn(
                relevant_postings[0],
                {
                    "type": "account",
                    "data": account_based_splitter["transfer_account"],
                },
            )

        return None

    for entry in entries:

        if not isinstance(entry, data.Transaction):
            continue

        new_txn = split_txn_metadata_based_splitter(entry)
        if new_txn is not None:
            new_entries.append(new_txn)

        new_txn = split_txn_account_based_splitter(config, entry)
        if new_txn is not None:
            new_entries.append(new_txn)

    return entries + new_entries, []
