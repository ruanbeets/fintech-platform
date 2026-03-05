def validate_transactions(df):

    if df.empty:
        raise ValueError("No transactions found in file")

    if "date" not in df.columns:
        raise ValueError("Missing date column")

    if "amount" not in df.columns:
        raise ValueError("Missing amount column")

    return True