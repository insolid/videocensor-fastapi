import uuid
from typing import Annotated

import yookassa as yk
from fastapi import APIRouter, HTTPException, Query

from app.api.deps.auth import CurrentUserDep
from app.core.config import settings
from app.core.db import SessionDep
from app.models.payments import Payment
from app.models.subscriptions import Subscription
from app.schemas.payments import (
    PaymentCreate,
    PaymentCreateResponse,
    PaymentQuery,
    PaymentRead,
)
from app.utils.fastcrud import CustomFastCRUD

yk.Configuration.account_id = settings.yookassa_account_id
yk.Configuration.secret_key = settings.yookassa_secret_key

from .subscriptions import plan_crud

router = APIRouter(prefix="", tags=["payments"])
payment_crud = CustomFastCRUD(Payment, updated_at_column="")


@router.get(
    "/payments",
    # response_model=list[PaymentRead],
    name="payments:list_payments",
)
async def list_payments(
    db: SessionDep,
    cur_user: CurrentUserDep,
    q: Annotated[PaymentQuery, Query()],
):
    return await payment_crud.get_multi(db, user_id=cur_user.id, **q.model_dump())


@router.get("/payments/{id}", response_model=PaymentRead, name="payments:get_payment")
async def get_payment(id: int, db: SessionDep, cur_user: CurrentUserDep):
    return await payment_crud.get(db, id=id, user_id=cur_user.id)


@router.post(
    "/plans/{plan_id}/buy-subscription",
    response_model=PaymentCreateResponse | dict[str, str],
    name="payments:buy_subscription",
)
async def buy_subscription(
    payment_data: PaymentCreate,
    db: SessionDep,
    cur_user: CurrentUserDep,
    plan_id: int,
):
    plan = await plan_crud.get(db, id=plan_id)
    sub = Subscription(user_id=cur_user.id, plan_id=plan_id)
    payment = Payment(
        amount=plan["price"],
        currency=plan["currency"],
        method="NEVERMIND",
        user_id=cur_user.id,
    )
    db.add_all([sub, payment])
    await db.flush()
    payment.subscription_id = sub.id

    try:
        yk_payment = yk.Payment.create(
            {
                "amount": {
                    "value": plan["price"],
                    "currency": plan["currency"].value,
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": payment_data.return_url,
                },
                "capture": True,
                "description": f'Payment for {plan["title"]}',
                "metadata": {
                    "payment_id": payment.id,
                    "subscription_id": sub.id,
                },
            },
            uuid.uuid4(),
        )
    except Exception as e:
        print(e)
        await db.rollback()
        raise HTTPException(400, "Something went wrong")

    await db.commit()

    return PaymentCreateResponse(
        confirmation_url=yk_payment.confirmation.confirmation_url
    )
