from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from app.models.subscriptions import Currency
from app.schemas.query import CommonQuery


class PlanQuery(CommonQuery):
    sort_by: Annotated[
        Literal["id", "created_at", "price"],
        Field(serialization_alias="sort_columns"),
    ] = "price"


class PlanCreate(BaseModel):
    title: str
    description: str
    duration_months: int
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    currency: Currency


class PlanUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    duration_months: int | None = None
    price: Annotated[Decimal | None, Field(gt=0, max_digits=10, decimal_places=2)] = (
        None
    )
    currency: Currency | None = None


class PlanRead(PlanCreate):
    id: int


class SubscriptionQuery(CommonQuery):
    sort_by: Annotated[
        Literal["id", "created_at"], Field(serialization_alias="sort_columns")
    ] = "created_at"


class SubscriptionCreate(BaseModel):
    plan_id: int


class SubscriptionRead(SubscriptionCreate):
    id: int
    is_active: bool
    start_date: date | None = None
    end_date: date | None = None
    user_id: int
