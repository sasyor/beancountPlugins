import ast
import collections
import copy

from beancount.core import data

__plugins__ = ['split_card_transactions']

SplitCardTransactionError = collections.namedtuple(
    "SplitCardTransactionError", "source message entry"
)


def split_card_transactions(entries, options_map, config_str=None):
    config = {
        "booking_date": 'booking-date',
        "booking_transfer_account": 'booking-transfer-account',
        "booking_posting_narration": "Card transaction booking",
    }

    if config_str and config_str.strip():
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

    meta_name_booking_date = config['booking_date']
    meta_name_booking_transfer_account = config['booking_transfer_account']
    booking_posting_narration = config['booking_posting_narration']

    errors = []
    new_entries = []

    for entry in entries:

        if not isinstance(entry, data.Transaction):
            continue

        relevant_postings = list(filter(
            filter_posting(meta_name_booking_date, meta_name_booking_transfer_account),
            entry.postings))

        if len(relevant_postings) != 1:
            continue

        original_posting_with_booking_date = relevant_postings[0]
        booking_date = original_posting_with_booking_date.meta[meta_name_booking_date]
        booking_transfer_account = original_posting_with_booking_date.meta[meta_name_booking_transfer_account]
        booking_unit_number = original_posting_with_booking_date.units.number
        booking_currency_number = original_posting_with_booking_date.units.currency
        del original_posting_with_booking_date.meta[meta_name_booking_date]
        del original_posting_with_booking_date.meta[meta_name_booking_transfer_account]

        # booking entry: create
        booking_entry = copy.deepcopy(entry)
        booking_entry = booking_entry._replace(
            payee=None,
            narration=booking_posting_narration,
            date=booking_date,
            postings=[original_posting_with_booking_date]
        )
        data.create_simple_posting(booking_entry, booking_transfer_account, -booking_unit_number,
                                   booking_currency_number)

        # existing entry: remove original posting with booking date
        entry.postings.remove(original_posting_with_booking_date)
        data.create_simple_posting(entry, booking_transfer_account, booking_unit_number, booking_currency_number)

        new_entries.append(booking_entry)

    return entries + new_entries, errors


def filter_posting(meta_name_booking_date, meta_name_booking_transfer_account):
    return lambda posting: meta_name_booking_date in posting.meta and meta_name_booking_transfer_account in posting.meta
