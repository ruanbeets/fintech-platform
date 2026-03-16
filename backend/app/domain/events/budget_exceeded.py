def check_budget_exceeded(spent, budget_limit):

    if spent > budget_limit:

        return {
            "event": "budget_exceeded",
            "spent": spent,
            "limit": budget_limit
        }

    return None