LARGE_TRANSACTION_THRESHOLD = 1000


def detect_large_transaction(transaction):

    if transaction.type == "expense" and transaction.amount >= LARGE_TRANSACTION_THRESHOLD:

        return {
            "event": "large_transaction",
            "amount": transaction.amount
        }

    return None