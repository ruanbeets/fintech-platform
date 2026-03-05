import pandas as pd


COLUMN_MAPPING = {
    "transaction_date": "date",
    "date": "date",
    "value": "amount",
    "amount": "amount",
    "description": "description",
    "merchant": "description",
}


def clean_transactions(df: pd.DataFrame):

    df = df.rename(columns=COLUMN_MAPPING)

    required_columns = ["date", "amount", "description"]

    df = df[required_columns]

    df["date"] = pd.to_datetime(df["date"])

    df["amount"] = pd.to_numeric(df["amount"])

    df = df.dropna()

    return df