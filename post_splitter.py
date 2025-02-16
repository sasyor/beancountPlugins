import ast

__plugins__ = ["post_splitter"]

from abc import abstractmethod

from beancount.core import data


class NoSplitter:
    def __init__(self, entry):
        self.entry = entry

    def split(self):
        return self.entry


class SplitterBase:

    def __init__(self, metadata_name_type, metadata_name_skip_split, roundings, entry, post_with_split_data):
        self.metadata_name_type = metadata_name_type
        self.roundings = roundings
        self.entry = entry
        self.post_with_split_data = post_with_split_data
        self.new_cost = None

    def split(self):
        del self.post_with_split_data.meta[self.metadata_name_type]

        new_postings = []
        for posting in self.entry.postings:
            if posting == self.post_with_split_data or not self.is_modify_needed(posting):
                new_postings.append(posting)
                continue

            new_unit = self.get_new_unit(posting)
            new_cost = self.new_cost

            new_posting = data.Posting(posting.account, new_unit, new_cost, None, None, posting.meta)
            new_postings.append(new_posting)

        return data.Transaction(self.entry.meta, self.entry.date, self.entry.flag, self.entry.payee,
                                self.entry.narration, self.entry.tags,
                                self.entry.links, new_postings)

    @abstractmethod
    def get_new_unit(self, posting):
        pass

    def round(self, number, currency):
        if self.roundings is None:
            return number

        decimals = self.roundings.get(currency)
        if decimals is None:
            return number

        return round(number, decimals)

    def is_modify_needed(self, posting):
        return posting.units.number == 0 and (posting.meta and "skip-split" not in posting.meta)


class EqualSplitter(SplitterBase):
    def __init__(self, metadata_name_type, metadata_name_skip_split, roundings, entry, post_with_split_data):
        super().__init__(metadata_name_type, metadata_name_skip_split, roundings, entry, post_with_split_data)

        divider = 0
        number = self.post_with_split_data.units.number
        for posting in entry.postings:
            if posting == post_with_split_data:
                continue

            if not self.is_modify_needed(posting):
                number += posting.units.number
            else:
                divider += 1

        number = number / divider
        number = self.round(number, self.post_with_split_data.units.currency)
        self.new_unit = data.Amount(
            -number,
            post_with_split_data.units.currency)

    def get_new_unit(self, posting):
        return self.new_unit


class ProportionSplitter(SplitterBase):
    def __init__(self, metadata_name_type, metadata_name_skip_split, metadata_name_split_ratio, roundings, entry,
                 post_with_split_data,
                 number_to_split, new_cost=None):
        super().__init__(metadata_name_type, metadata_name_skip_split, roundings, entry, post_with_split_data)

        self.metadata_name_split_ratio = metadata_name_split_ratio
        self.number_to_split = number_to_split
        self.new_cost = new_cost

        self.max_number = 0
        for posting in entry.postings:
            if self.metadata_name_split_ratio in posting.meta:
                self.max_number += posting.meta[self.metadata_name_split_ratio].number

    def get_new_unit(self, posting):
        number = posting.meta[self.metadata_name_split_ratio].number / self.max_number * self.number_to_split
        number = self.round(number, posting.meta[self.metadata_name_split_ratio].currency)
        return data.Amount(number,
                           posting.meta[self.metadata_name_split_ratio].currency)

    def is_modify_needed(self, posting):
        return self.metadata_name_split_ratio in posting.meta


class PostSplitter:

    def __init__(self, options_map, config_str=""):
        config = {}
        expr = ast.literal_eval(config_str)
        config.update(expr)

        self.roundings = config.get("roundings")
        self.metadata_name_type = config["metadata-name-type"]
        self.metadata_name_skip_split = config.get("metadata-name-skip-split")
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

            new_entry = self.get_splitter(entry, post_with_split_data).split()

            new_entries.append(new_entry)

        return new_entries, []

    def get_splitter(self, entry, post_with_split_data):
        if post_with_split_data.meta[self.metadata_name_type] == "equal":
            return EqualSplitter(self.metadata_name_type, self.metadata_name_skip_split, self.roundings, entry,
                                 post_with_split_data)
        elif (post_with_split_data.meta[self.metadata_name_type] == "proportional"
              and self.metadata_name_split_ratio is not None):
            return self.get_proportion_splitter(entry, post_with_split_data)
        else:
            return NoSplitter(entry)

    def get_proportion_splitter(self, entry, post_with_split_data):
        if (self.metadata_name_unit is not None
                and self.metadata_name_exchange_rate is not None
                and self.metadata_name_unit in post_with_split_data.meta
                and self.metadata_name_exchange_rate in post_with_split_data.meta):
            number_to_split = post_with_split_data.meta[self.metadata_name_unit].number
            exchange_rate = post_with_split_data.meta[self.metadata_name_exchange_rate]
            new_cost = data.Cost(exchange_rate.number, exchange_rate.currency, entry.date, None)
            del post_with_split_data.meta[self.metadata_name_exchange_rate]
            return ProportionSplitter(self.metadata_name_type, self.metadata_name_skip_split,
                                      self.metadata_name_split_ratio,
                                      self.roundings, entry, post_with_split_data, number_to_split, new_cost)
        else:
            number_to_split = -post_with_split_data.units.number
            return ProportionSplitter(self.metadata_name_type, self.metadata_name_skip_split,
                                      self.metadata_name_split_ratio,
                                      self.roundings, entry, post_with_split_data, number_to_split)


def post_splitter(entries, options_map, config_str=""):
    post_splitter_obj = PostSplitter(options_map, config_str)
    return post_splitter_obj.split(entries)
