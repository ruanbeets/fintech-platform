def validate_transactions(df):

    if df.empty:
        raise ValueError("No transactions found in file")

    required = ["date", "amount"]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing {col} column")

    return True