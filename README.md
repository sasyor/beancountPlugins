# Beancount plugins

---

## Split card transactions

### Use case

Payment with card results in 2 dates:

- Transaction date: when the actual card usage happened.
- Booking date: when the bank books the card usage.

E.g. you pay by card to buy some clothing on `2013-05-31` and the bank will book it `2013-06-03`. So in reality 2 transaction happened, one where the expense happened (buying the clothes on `2013-05-31`) and one where the bank booked the transaction (`2013-06-03`).
The first transaction is needed to accurately track the expenses, the second one is needed to match up with the bank statements.

### How to use

```
plugin "plugins.split_card_transactions" "{
    'booking_posting_narration': 'Some custom narration'
}"
```

#### Example

Input:

```
2013-05-31 * "Paid by card"
    Assets:Bank:Checking      -100 USD
        booking-transfer-account: Assets:Bank:DebitCard
        booking-date: 2013-06-03
    Expense:Clothing           100 USD
```

Result:

```
2013-05-31 * "Paid by card"
    Assets:Bank:DebitCard     -100 USD
    Expense:Clothing           100 USD

2013-06-03 * "Some custom narration"
    Assets:Bank:Checking      -100 USD
    Assets:Bank:DebitCard      100 USD
```
