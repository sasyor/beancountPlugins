from beancount.core import data

from .value_getter import ValueGetter


class MetadataValueGetter(ValueGetter):
    def __init__(self, metadata_name: str) -> None:
        self.metadata_name = metadata_name

    def get_value(self, posting: data.Posting) -> str:
        return posting.meta.get(self.metadata_name)
