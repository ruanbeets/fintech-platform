"""Typed financial trends and explainable recurring-behaviour response."""
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel


class Comparison(BaseModel):
    baseline: Decimal | None
    absolute_change: Decimal | None
    percentage_change: Decimal | None
    coverage: str


class CategoryMonth(BaseModel):
    month: str
    spend: Decimal
    coverage: str
    partial_month: bool


class CategoryTrend(BaseModel):
    category: str
    current_spend: Decimal
    previous_spend: Decimal
    change: Comparison
    trailing_3_month_average: Decimal | None
    trailing_6_month_average: Decimal | None
    share_of_expenses: Decimal | None
    history: list[CategoryMonth]


class IncomeExtreme(BaseModel):
    month: str
    income: Decimal


class IncomeTrend(BaseModel):
    current: Decimal
    previous_month: Comparison
    versus_3_month_average: Comparison
    versus_6_month_average: Comparison
    average_12_month: Decimal | None
    recorded_months: int
    highest_month: IncomeExtreme | None
    lowest_month: IncomeExtreme | None
    coverage_note: str


class RateMonth(BaseModel):
    month: str
    savings_rate: Decimal | None
    coverage: str
    partial_month: bool


class RateAverage(BaseModel):
    value: Decimal | None
    valid_months: int
    window_months: int


class SavingsTrend(BaseModel):
    current: Decimal | None
    previous_valid: RateMonth | None
    change_percentage_points: Decimal | None
    trailing_3_month_average: RateAverage
    trailing_6_month_average: RateAverage
    history: list[RateMonth]
    methodology: str


class RecurringItem(BaseModel):
    normalized_name: str
    account_id: str
    transaction_type: Literal["income", "expense", "transfer"]
    category: str
    typical_amount: Decimal
    frequency: Literal["monthly", "weekly", "fortnightly"]
    strength: Literal["likely", "strong"]
    first_observed: str
    most_recent: str
    occurrence_count: int
    expected_next_occurrence: str | None
    next_occurrence_note: str
    evidence: str


class SpendingClass(BaseModel):
    classification: Literal["fixed_recurring", "variable", "unclassified"]
    amount: Decimal
    share: Decimal | None
    transaction_count: int
    explanation: str


class SpendingBreakdown(BaseModel):
    total_expenses: Decimal
    classes: list[SpendingClass]
    methodology: str


class FinancialTrends(BaseModel):
    categories: list[CategoryTrend]
    income: IncomeTrend
    savings: SavingsTrend
    recurring: list[RecurringItem]
    spending: SpendingBreakdown
    recurring_methodology: str
    observed_through: str
