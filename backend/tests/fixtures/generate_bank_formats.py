"""Synthetic ledgers only; fixed amounts independently specified in importer tests."""
import csv
from pathlib import Path

ROOT = Path(__file__).parent
HEADERS = ["Nr", "Account", "Posting Date", "Transaction Date", "Description", "Original Description",
           "Parent Category", "Category", "Money In", "Money Out", "Fee", "Balance"]
LEDGER = [
    ["1", "0000123400", "2026-08-01", "2026-07-31", "Synthetic salary", "PAYROLL SYNTHETIC", "Income", "Salary", "3000.00", "", "", "4000.00"],
    ["2", "0000123400", "2026-08-02", "2026-08-01", "Synthetic groceries", "GROCER SYNTHETIC", "Living", "Groceries", "", "-500.00", "", "3500.00"],
    ["3", "0000123400", "2026-08-03", "2026-08-03", "Synthetic bank charge", "FEE SYNTHETIC", "Banking", "Bank fees", "", "", "-3.00", "3497.00"],
    ["4", "0000123400", "2026-08-04", "2026-08-04", "Synthetic incoming transfer", "OWN ACCOUNT", "Transfers", "Savings", "200.00", "", "", "3697.00"],
    ["5", "0000123400", "2026-08-05", "2026-08-05", "Synthetic savings transfer", "OWN ACCOUNT", "Savings", "Transfer", "", "-400.00", "", "3297.00"],
    ["6", "0000123400", "2026-08-06", "2026-08-06", "Synthetic cafe", "CAFE SYNTHETIC", "Living", "Dining", "", "-25.00", "", "3272.00"],
    ["7", "0000123400", "2026-08-06", "2026-08-06", "Synthetic cafe", "CAFE SYNTHETIC", "Living", "Dining", "", "-25.00", "", "3247.00"],
]


def generate():
    from decimal import Decimal
    for name, model, delimiter in [("bank_signed.csv", "signed", ","), ("bank_debit_credit.csv", "debit", ","),
                                    ("bank_money.csv", "money", ","), ("bank_reference.csv", "reference", ","),
                                    ("bank_european.csv", "euro", ";"), ("bank_tab.csv", "reference", "\t")]:
        with (ROOT / name).open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=delimiter)
            if model in {"reference", "euro"}:
                writer.writerow(["Synthetic personal statement — no real financial data"])
                writer.writerow(HEADERS)
            else:
                writer.writerow(["Date", "Description"] + (["Amount", "Fee"] if model == "signed" else ["Debit", "Credit", "Fee"] if model == "debit" else ["Money In", "Money Out", "Fee"]) + ["Balance", "Parent Category", "Category", "Harmless Extra"])
            for row in LEDGER:
                movement = sum((Decimal(row[i] or "0") for i in (8, 9, 10)))
                if model in {"reference", "euro"}:
                    output = list(row)
                    if model == "euro":
                        output[8:] = [v.replace(".", ",") for v in output[8:]]
                else:
                    amounts = [str(movement), row[10]] if model == "signed" else [row[9].lstrip("-"), row[8], row[10].lstrip("-")] if model == "debit" else row[8:11]
                    output = [row[2], row[4]] + amounts + [row[11], row[6], row[7], "ignored"]
                writer.writerow(output)
            if name == "bank_reference.csv":
                writer.writerow(["8", "0000123400", "2026-08-07", "2026-08-07", "Malformed synthetic row", "NOTE", "", "", "", "", "", ""])


if __name__ == "__main__":
    generate()
