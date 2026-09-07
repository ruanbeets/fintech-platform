from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TransactionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: UUID
    account_id: UUID
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2, allow_inf_nan=False)
    type: Literal["income", "expense", "transfer"]
    occurred_at: datetime
    category: str | None = None
    merchant: str | None = None
    description: str | None = None

    @field_validator("occurred_at")
    @classmethod
    def normalize_date(cls, value):
        return value.astimezone(timezone.utc).replace(tzinfo=None) if value.tzinfo else value


class TransactionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2, allow_inf_nan=False)
    type: Literal["income", "expense", "transfer"] | None = None
    occurred_at: datetime | None = None
    category: str | None = None
    merchant: str | None = None
    description: str | None = None

    @model_validator(mode="after")
    def validate_required_values(self):
        for name in {"amount", "type", "occurred_at"} & self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null")
        if self.occurred_at and self.occurred_at.tzinfo:
            self.occurred_at = self.occurred_at.astimezone(timezone.utc).replace(tzinfo=None)
        return self
