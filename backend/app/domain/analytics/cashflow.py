def calculate_cashflow(transactions):

    income = 0
    expenses = 0

    for t in transactions:

        if t.type == "income":
            income += t.amount

        else:
            expenses += t.amount

    return {
        "income": income,
        "expenses": expenses,
        "net": income - expenses
    }