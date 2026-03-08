import datetime
import decimal


class Transaction:
    def __init__(self, date: datetime.date, amount: decimal.Decimal):
        self.date = date
        self.amount = amount
