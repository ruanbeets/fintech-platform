from pydantic import BaseModel


class MonthlySpending(BaseModel):
    month: str
    total: float


class Cashflow(BaseModel):
    income: float
    expenses: float
    net: float


class ForecastPoint(BaseModel):
    month: str
    projected_balance: float