from pydantic import BaseModel
from uuid import UUID


class AccountBalance(BaseModel):
    account_id: UUID
    account_name: str
    balance: float


class DashboardSummary(BaseModel):
    total_balance: float
    monthly_income: float
    monthly_expenses: float
    savings_rate: float


class CategorySpending(BaseModel):
    category: str
    amount: float


class DashboardResponse(BaseModel):
    summary: DashboardSummary
    accounts: list[AccountBalance]
    category_breakdown: list[CategorySpending]