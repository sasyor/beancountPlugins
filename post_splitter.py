import ast

__plugins__ = ["post_splitter"]

from beancount.core import data


class PostSplitter:

    def __init__(self, options_map, config_str=""):
        config = {}
        expr = ast.literal_eval(config_str)
        config.update(expr)

        self.roundings = config.get("roundings")
        self.metadata_name_type = config["metadata-name-type"]
        self.metadata_name_unit = config.get("metadata-name-unit")
        self.metadata_name_exchange_rate = config.get("metadata-name-exchange-rate")
        self.metadata_name_split_ratio = config.get("metadata-name-split-ratio")

    def split(self, entries):
        new_entries = []
        for entry in entries:
            if not isinstance(entry, data.Transaction):
                new_entries.append(entry)
                continue

            post_with_split_data = list(filter(lambda
                                                   posting: posting.meta
                                                            and self.metadata_name_type in posting.meta,
                                               entry.postings))
            if len(post_with_split_data) != 1:
                new_entries.append(entry)
                continue

            post_with_split_data = post_with_split_data[0]

            if post_with_split_data.meta[self.metadata_name_type] == "equal":
                new_entry = self.split_equal(entry, post_with_split_data)
                new_entries.append(new_entry)
            elif (post_with_split_data.meta[self.metadata_name_type] == "proportional"
                  and self.metadata_name_split_ratio is not None):
                if (self.metadata_name_unit is not None
                        and self.metadata_name_exchange_rate is not None
                        and self.metadata_name_unit in post_with_split_data.meta
                        and self.metadata_name_exchange_rate in post_with_split_data.meta):
                    new_entry = self.split_proportional_with_cost(entry, post_with_split_data)
                else:
                    new_entry = self.split_proportional(entry, post_with_split_data)
                new_entries.append(new_entry)
            else:
                new_entries.append(entry)

        return new_entries, []

    def split_equal(self, entry, post_with_split_data):
        number = -post_with_split_data.units.number / (len(entry.postings) - 1)
        number = self.round(number, post_with_split_data.units.currency)
        new_unit = data.Amount(
            number,
            post_with_split_data.units.currency)

        new_postings = []
        for posting in entry.postings:
            if posting == post_with_split_data:
                del posting.meta[self.metadata_name_type]
                new_postings.append(posting)
                continue

            new_posting = data.Posting(posting.account, new_unit, None, None, None, posting.meta)
            new_postings.append(new_posting)

        return data.Transaction(entry.meta, entry.date, entry.flag, entry.payee, entry.narration, entry.tags,
                                entry.links, new_postings)

    def split_proportional(self, entry, post_with_split_data):
        number_to_split = -post_with_split_data.units.number

        return self.split_proportional_internal(entry, None, number_to_split, post_with_split_data)

    def split_proportional_with_cost(self, entry, post_with_split_data):
        number_to_split = post_with_split_data.meta[self.metadata_name_unit].number
        exchange_rate = post_with_split_data.meta[self.metadata_name_exchange_rate]
        new_cost = data.Cost(exchange_rate.number, exchange_rate.currency, entry.date, None)

        del post_with_split_data.meta[self.metadata_name_exchange_rate]

        return self.split_proportional_internal(entry, new_cost, number_to_split, post_with_split_data)

    def split_proportional_internal(self, entry, new_cost, number_to_split, post_with_split_data):
        max_number = 0
        for posting in entry.postings:
            if self.metadata_name_split_ratio in posting.meta:
                max_number += posting.meta[self.metadata_name_split_ratio].number
        new_postings = []
        for posting in entry.postings:
            if posting == post_with_split_data:
                del posting.meta[self.metadata_name_type]
                new_postings.append(posting)
                continue

            number = posting.meta[self.metadata_name_split_ratio].number / max_number * number_to_split
            number = self.round(number, posting.meta[self.metadata_name_split_ratio].currency)
            new_unit = data.Amount(number,
                                   posting.meta[self.metadata_name_split_ratio].currency)
            new_posting = data.Posting(posting.account, new_unit, new_cost, None, None, posting.meta)
            new_postings.append(new_posting)
        return data.Transaction(entry.meta, entry.date, entry.flag, entry.payee, entry.narration, entry.tags,
                                entry.links, new_postings)

    def round(self, number, currency):
        if self.roundings is None:
            return number

        decimals = self.roundings.get(currency)
        if decimals is None:
            return number

        return round(number, decimals)


def post_splitter(entries, options_map, config_str=""):
    post_splitter_obj = PostSplitter(options_map, config_str)
    return post_splitter_obj.split(entries)
