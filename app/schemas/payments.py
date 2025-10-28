from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.query import CommonQuery


class PaymentCreate(BaseModel):
    return_url: str


class PaymentCreateResponse(BaseModel):
    confirmation_url: HttpUrl


class PaymentRead(PaymentCreate):
    id: int
    status: str
    amount: Decimal
    currency: str
    method: str
    subscription_id: int


class PaymentQuery(CommonQuery):
    sort_by: Annotated[
        Literal["id", "created_at"], Field(serialization_alias="sort_columns")
    ] = "created_at"
