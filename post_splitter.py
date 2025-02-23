import ast

__plugins__ = ["post_splitter"]

from abc import abstractmethod
from copy import deepcopy

from beancount.core import data


class SplitDataBase:
    def __init__(self, metadata_name_type):
        self.metadata_name_type = metadata_name_type

    def is_modify_needed(self, posting):
        return True

    @abstractmethod
    def before_split(self):
        pass


class EntryWithSplitData(SplitDataBase):
    def __init__(self, entry, metadata_name_type):
        super().__init__(metadata_name_type)
        self.entry = entry

    def before_split(self):
        if self.metadata_name_type is not None:
            del self.entry.meta[self.metadata_name_type]


class PostWithSplitData(SplitDataBase):
    def __init__(self, metadata_name_type, post_with_split_data):
        super().__init__(metadata_name_type)
        self.post_with_split_data = post_with_split_data

    def is_modify_needed(self, posting):
        return posting != self.post_with_split_data

    def before_split(self):
        del self.post_with_split_data.meta[self.metadata_name_type]


class NoSplitter:
    def __init__(self, entry):
        self.entry = entry

    def split(self):
        return self.entry


class SplitterBase:

    def __init__(self, metadata_name_skip_split, roundings, entry, split_data):
        self.roundings = roundings
        self.entry = entry
        self.split_data = split_data
        self.new_cost = None

    def split(self):
        self.split_data.before_split()

        new_postings = []
        for posting in self.entry.postings:
            if not self.split_data.is_modify_needed(posting) or not self.is_modify_needed(posting):
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
        split_data = PostWithSplitData(metadata_name_type, post_with_split_data)
        super().__init__(metadata_name_skip_split, roundings, entry, split_data)

        divider = 0
        number = post_with_split_data.units.number
        for posting in entry.postings:
            if posting == post_with_split_data:
                continue

            if not self.is_modify_needed(posting):
                number += posting.units.number
            else:
                divider += 1

        number = number / divider
        number = self.round(number, post_with_split_data.units.currency)
        self.new_unit = data.Amount(
            -number,
            post_with_split_data.units.currency)

    def get_new_unit(self, posting):
        return self.new_unit


class ProportionSplitDataBase:
    def get_number(self, posting):
        return posting.units.number

    def get_currency(self, posting):
        return posting.units.currency

    def is_modify_needed(self, posting):
        return True


class MetadataProportionSplitData(ProportionSplitDataBase):
    def __init__(self, metadata_name_split_ratio):
        self.metadata_name_split_ratio = metadata_name_split_ratio

    def get_number(self, posting):
        return posting.meta[self.metadata_name_split_ratio].number

    def get_currency(self, posting):
        return posting.meta[self.metadata_name_split_ratio].currency

    def is_modify_needed(self, posting):
        return self.metadata_name_split_ratio in posting.meta


class DiscountProportionSplitData(ProportionSplitDataBase):
    def __init__(self, discount_id):
        self.discount_id = discount_id

    def is_modify_needed(self, posting):
        return "discount-ids" in posting.meta and str(self.discount_id) in posting.meta["discount-ids"].split(",")


class ProportionSplitter(SplitterBase):
    def __init__(self, metadata_name_skip_split, proportion_split_data, roundings, entry,
                 split_data,
                 number_to_split, new_cost=None):
        super().__init__(metadata_name_skip_split, roundings, entry, split_data)

        self.proportion_split_data = proportion_split_data
        self.number_to_split = number_to_split
        self.new_cost = new_cost

        self.max_number = 0
        for posting in entry.postings:
            if self.proportion_split_data.is_modify_needed(posting):
                self.max_number += self.proportion_split_data.get_number(posting)

    def get_new_unit(self, posting):
        number = self.proportion_split_data.get_number(posting) / self.max_number * self.number_to_split
        number = self.round(number, self.proportion_split_data.get_currency(posting))
        return data.Amount(number,
                           self.proportion_split_data.get_currency(posting))

    def is_modify_needed(self, posting):
        return self.proportion_split_data.is_modify_needed(posting)


class DiscountSplitter:
    def __init__(self, metadata_name_type, metadata_name_skip_split, roundings):
        self.metadata_name_type = metadata_name_type
        self.metadata_name_skip_split = metadata_name_skip_split
        self.roundings = roundings

    def split(self, entry):
        new_entry = entry

        discount_id = 1
        while "discount-" + str(discount_id) in entry.meta:
            new_entry = self.__single_split(new_entry, discount_id)
            discount_id += 1

        return new_entry

    def __single_split(self, entry, discount_id):
        number_to_split = -entry.meta["discount-" + str(discount_id)].number

        new_postings = []
        for posting in entry.postings:
            if not "discount-ids" in posting.meta or str(discount_id) not in posting.meta["discount-ids"].split(","):
                new_postings.append(posting)
                continue

            shared_meta = {}
            for key, value in posting.meta.items():
                if key != "discount-ids":
                    shared_meta[key] = value

            new_postings.append(self.__create_original_posting(discount_id, shared_meta, posting))
            new_postings.append(self.__create_discount_posting(discount_id, shared_meta, posting))

        new_entry = data.Transaction(entry.meta, entry.date, entry.flag, entry.payee,
                                     entry.narration, entry.tags,
                                     entry.links, new_postings)

        split_data = EntryWithSplitData(new_entry, self.metadata_name_type if discount_id == 1 else None)
        proportion_split_data = DiscountProportionSplitData(discount_id)
        new_entry = ProportionSplitter(self.metadata_name_skip_split, proportion_split_data,
                                       self.roundings, new_entry, split_data, number_to_split).split()

        return new_entry

    @staticmethod
    def __create_discount_posting(discount_id, shared_meta, posting):
        new_account = ":".join(posting.account.split(':')[:-1] + ["Discount"])
        new_meta = deepcopy(shared_meta)
        new_meta["discount-ids"] = str(discount_id)
        return data.Posting(new_account, posting.units, posting.cost, None, None, new_meta)

    @staticmethod
    def __create_original_posting(discount_id, shared_meta, posting):
        new_meta = deepcopy(shared_meta)
        if "," in posting.meta["discount-ids"]:
            new_meta["discount-ids"] = ",".join(
                filter(lambda v: v != str(discount_id), posting.meta["discount-ids"].split(",")))
        return data.Posting(posting.account, posting.units, posting.cost, None, None, new_meta)


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
            new_entry = self.__split_single_entry(entry)
            new_entries.append(new_entry)

        return new_entries, []

    def __split_single_entry(self, entry):
        if not isinstance(entry, data.Transaction):
            return entry

        if entry.meta and self.metadata_name_type in entry.meta:
            return self.__get_entry_level_splitter().split(entry)

        post_with_split_data = list(filter(lambda
                                               posting: posting.meta
                                                        and self.metadata_name_type in posting.meta,
                                           entry.postings))
        if len(post_with_split_data) != 1:
            return entry

        post_with_split_data = post_with_split_data[0]
        return self.__get_posting_level_splitter(entry, post_with_split_data).split()

    def __get_entry_level_splitter(self):
        return DiscountSplitter(self.metadata_name_type, self.metadata_name_split_ratio, self.roundings)

    def __get_posting_level_splitter(self, entry, post_with_split_data):
        if post_with_split_data.meta[self.metadata_name_type] == "equal":
            return EqualSplitter(self.metadata_name_type, self.metadata_name_skip_split, self.roundings, entry,
                                 post_with_split_data)
        elif (post_with_split_data.meta[self.metadata_name_type] == "proportional"
              and self.metadata_name_split_ratio is not None):
            return self.__get_proportion_splitter(entry, post_with_split_data)
        else:
            return NoSplitter(entry)

    def __get_proportion_splitter(self, entry, post_with_split_data):
        split_data = PostWithSplitData(self.metadata_name_type, post_with_split_data)
        proportion_split_data = MetadataProportionSplitData(self.metadata_name_split_ratio)
        if (self.metadata_name_unit is not None
                and self.metadata_name_exchange_rate is not None
                and self.metadata_name_unit in post_with_split_data.meta
                and self.metadata_name_exchange_rate in post_with_split_data.meta):
            number_to_split = post_with_split_data.meta[self.metadata_name_unit].number
            exchange_rate = post_with_split_data.meta[self.metadata_name_exchange_rate]
            new_cost = data.Cost(exchange_rate.number, exchange_rate.currency, entry.date, None)
            del post_with_split_data.meta[self.metadata_name_exchange_rate]
            return ProportionSplitter(self.metadata_name_skip_split,
                                      proportion_split_data,
                                      self.roundings, entry, split_data, number_to_split, new_cost)
        else:
            number_to_split = -post_with_split_data.units.number
            return ProportionSplitter(self.metadata_name_skip_split,
                                      proportion_split_data,
                                      self.roundings, entry, split_data, number_to_split)


def post_splitter(entries, options_map, config_str=""):
    post_splitter_obj = PostSplitter(options_map, config_str)
    return post_splitter_obj.split(entries)
