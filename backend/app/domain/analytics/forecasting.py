from datetime import timedelta


def forecast_balance(current_balance, monthly_net, months=6):

    projections = []

    balance = current_balance

    for i in range(1, months + 1):

        balance += monthly_net

        projections.append({
            "month": i,
            "projected_balance": balance
        })

    return projections