from decimal import Decimal
from typing import Dict


class Rounder:
    roundings: Dict[str, int]

    def __init__(self, roundings: Dict[str, int]) -> None:
        self.roundings = roundings

    def round(self, number: int, currency: str) -> Decimal:
        if self.roundings is None:
            return Decimal(number)

        decimals = self.roundings.get(currency)
        if decimals is None:
            return Decimal(number)

        return Decimal(round(number, decimals))
