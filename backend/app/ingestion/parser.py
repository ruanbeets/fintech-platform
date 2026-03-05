import pandas as pd
from io import BytesIO


def parse_file(filename: str, contents: bytes):

    if filename.endswith(".csv"):
        df = pd.read_csv(BytesIO(contents))

    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(BytesIO(contents))

    else:
        raise ValueError("Unsupported file type")

    return df