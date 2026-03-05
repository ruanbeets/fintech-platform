def validate_transactions(df):

    if "date" not in df.columns:
        raise ValueError("Missing date column")

    if "amount" not in df.columns:
        raise ValueError("Missing amount column")

    if df["amount"].isnull().any():
        raise ValueError("Invalid amount values")

    return True