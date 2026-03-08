import calendar
import datetime
import decimal

from .transaction import Transaction


class MonthlyTracker:
    def __init__(self, year_number: int, month_number: int):
        self.transactions: dict[datetime.date, Transaction] = {}

        self.year_number = year_number
        self.month_number = month_number
        self.max_day_number = calendar.monthrange(year_number, month_number)[1]

    def add(self, daily_rate: decimal.Decimal):
        date = datetime.date.fromisocalendar(self.year_number, self.month_number, self.max_day_number)
        self.transactions[date] = Transaction(date, daily_rate * self.max_day_number)

    def add_with_start_date(self, daily_rate: decimal.Decimal, start_day_number: int):
        date = datetime.date.fromisocalendar(self.year_number, self.month_number, self.max_day_number)
        self.transactions[date] = Transaction(date, daily_rate * (self.max_day_number - start_day_number))

    def add_with_end_date(self, daily_rate: decimal.Decimal, end_day_number: int):
        date = datetime.date.fromisocalendar(self.year_number, self.month_number, end_day_number)
        self.transactions[date] = Transaction(date, daily_rate * end_day_number)
