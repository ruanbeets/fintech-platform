def handle_transaction_created(transaction):

    events = []

    if transaction.amount > 1000 and transaction.type == "expense":

        events.append({
            "event": "large_transaction",
            "transaction_id": str(transaction.id)
        })

    return events