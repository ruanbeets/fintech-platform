from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class Mapping(BaseModel):
    model_config = ConfigDict(extra="forbid")
    date: int | None = None
    description: int | None = None
    amount: int | None = None
    debit: int | None = None
    credit: int | None = None
    currency: int | None = None
    category: int | None = None
    balance: int | None = None
    transaction_type: int | None = None


class ReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sheet: str
    header_row: int = Field(ge=1, le=50)
    mapping: Mapping
    account: str = Field(min_length=1, max_length=80)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    date_order: Literal["DMY", "MDY", "YMD"]
    number_format: Literal["dot", "comma"]
    sign_convention: Literal["negative_expense", "positive_expense"]
    type_overrides: dict[int, Literal["income", "expense", "transfer"]] = Field(default_factory=dict)
    excluded_rows: list[int] = Field(default_factory=list, max_length=5000)


class NormalizedRow(BaseModel):
    source_row: int
    date: datetime
    description: str
    amount: Decimal
    transaction_type: Literal["income", "expense", "transfer"]
    category: str | None
    currency: str
    account: str
    balance_optional: Decimal | None = None
    source_file: str
    import_batch_id: UUID
    confidence: Literal["review_required"] = "review_required"


class RowResult(BaseModel):
    source_row: int
    status: Literal["valid", "invalid", "duplicate", "excluded"]
    errors: list[str] = Field(default_factory=list)
    transaction: NormalizedRow | None = None


class ReviewResponse(BaseModel):
    batch_id: UUID
    review_id: str
    detected: int
    valid: int
    invalid: int
    duplicates: int
    excluded: int
    to_import: int
    income: Decimal
    expenses: Decimal
    net_cash_flow: Decimal
    currency: str
    rows: list[RowResult]
    warning: str


class ConfirmRequest(BaseModel):
    review_id: str
    confirmed: Literal[True]
    skip_invalid: bool = False


class ConfirmResponse(BaseModel):
    batch_id: UUID
    imported: int
    duplicates: int
    skipped_invalid: int
    excluded: int
    message: str

class ColumnSuggestion(BaseModel):
    column: int | None
    confidence: Literal["high", "ambiguous", "unmapped"]
    candidates: list[int]


class DetectionResponse(BaseModel):
    batch_id: UUID
    file_type: Literal["csv", "xlsx", "xls", "xlsb", "ods", "pdf"]
    sheets: list[str]
    sheet: str
    header_row: int
    headers: list[str]
    mapping: dict[str, ColumnSuggestion]
    preview: list[list[str]]
    row_count: int


class SessionResponse(BaseModel):
    token: str
    expires_at: datetime
