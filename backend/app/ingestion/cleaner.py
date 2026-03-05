import pandas as pd


def clean_transactions(df: pd.DataFrame):

    # CAPITEC FORMAT
    if "Money In" in df.columns and "Money Out" in df.columns:

        df["Money In"] = pd.to_numeric(df["Money In"], errors="coerce")
        df["Money Out"] = pd.to_numeric(df["Money Out"], errors="coerce")

        if "Fee" in df.columns:
            df["Fee"] = pd.to_numeric(df["Fee"], errors="coerce")
        else:
            df["Fee"] = 0

        df["amount"] = (
            df["Money In"].fillna(0)
            + df["Money Out"].fillna(0)
            + df["Fee"].fillna(0)
        )

        df = df.rename(columns={
            "Transaction Date": "date",
            "Description": "description",
            "Category": "category",
            "Balance": "balance"
        })

    # EASY EQUITIES FORMAT
    elif "Debit/Credit" in df.columns:

        df = df.rename(columns={
            "Date": "date",
            "Comment": "description",
            "Debit/Credit": "amount"
        })

        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df["category"] = None
        df["balance"] = None

    else:
        raise ValueError("Unknown file format")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    if "balance" in df.columns:
        df["balance"] = pd.to_numeric(df["balance"], errors="coerce")

    df = df.dropna(subset=["date", "amount"])

    df = df[["date", "amount", "balance", "description", "category"]]

    return df