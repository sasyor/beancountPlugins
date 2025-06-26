from beancount.core import data

from .value_getter import ValueGetter


class FixedValueGetter(ValueGetter):
    def __init__(self, value: str):
        self.value = value

    def get_value(self, posting: data.Posting) -> str:
        return self.value
