from .rules_engine import categorize


def classify_transaction(transaction):

    category_name = categorize(transaction.description)

    return category_name