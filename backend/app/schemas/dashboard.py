"""Decimal financial values serialize as exact decimal strings."""
from decimal import Decimal
from pydantic import BaseModel
from app.schemas.trends import FinancialTrends


class RollingAverage(BaseModel):
    months: int
    income: Decimal | None = None
    expenses: Decimal | None = None
    net_cash_flow: Decimal | None = None
    savings_rate: Decimal | None = None
    recorded_months: int
    status: str


class MonthlyValues(BaseModel):
    month: str
    income: Decimal
    expenses: Decimal
    net_cash_flow: Decimal
    savings_rate: Decimal | None
    transaction_count: int
    coverage: str
    partial_month: bool
    trailing_3_month: RollingAverage
    trailing_6_month: RollingAverage


class UnavailableValue(BaseModel):
    value: Decimal | None = None
    status: str = "unavailable"
    reason: str


class AccountBalance(UnavailableValue):
    account_id: str
    name: str
    currency: str


class DashboardSummary(BaseModel):
    trends: FinancialTrends
    currency: str
    available_currencies: list[str]
    selected_month: str
    available_months: list[str]
    as_of: str
    demo: bool = False
    selected: MonthlyValues
    history: list[MonthlyValues]
    account_balances: list[AccountBalance]
    net_worth: UnavailableValue
    coverage_note: str
    # Retain lifetime fields for existing consumers, separated by currency.
    income: Decimal
    expense: Decimal
    net: Decimal
