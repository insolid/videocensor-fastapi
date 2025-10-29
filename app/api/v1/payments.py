import datetime
import uuid
from typing import Annotated

import yookassa as yk
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    Query,
    Request,
)
from pydantic import HttpUrl
from sqlalchemy.orm import selectinload

from app.api.deps.auth import CurrentUserDep
from app.core.config import settings
from app.core.db import SessionDep
from app.models.payments import Payment, Status
from app.models.subscriptions import Plan, Subscription
from app.schemas.payments import PaymentCreateResponse, PaymentQuery, PaymentRead
from app.utils.fastcrud import CustomFastCRUD

from ..deps.payments import is_yookassa_ip

yk.Configuration.account_id = settings.yookassa_account_id
yk.Configuration.secret_key = settings.yookassa_secret_key

from .subscriptions import plan_crud

router = APIRouter(prefix="", tags=["payments"])
payment_crud = CustomFastCRUD(Payment, updated_at_column="")


@router.get(
    "/payments",
    response_model=list[PaymentRead],
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
    response_model=PaymentCreateResponse | dict,
    name="payments:buy_subscription",
)
async def buy_subscription(
    return_url: Annotated[HttpUrl, Body(embed=True)],
    db: SessionDep,
    cur_user: CurrentUserDep,
    plan_id: int,
):
    plan = await plan_crud.get(db, id=plan_id)
    sub = Subscription(user_id=cur_user.id, plan_id=plan_id)
    payment = Payment(
        amount=plan["price"],
        currency=plan["currency"],
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
                    "return_url": return_url,
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
        raise HTTPException(400, "Something went wrong")

    await db.commit()

    return PaymentCreateResponse(
        confirmation_url=yk_payment.confirmation.confirmation_url
    )


@router.post(
    "/webhooks/yookassa",
    name="payments:yookassa_webhook",
    dependencies=[Depends(is_yookassa_ip)],
    status_code=200,
)
async def yookassa_webhook(bg_tasks: BackgroundTasks, req: Request, db: SessionDep):
    payload = await req.json()

    payment_id = int(payload["object"]["metadata"]["payment_id"])
    subscription_id = int(payload["object"]["metadata"]["subscription_id"])

    payment = await db.get(Payment, payment_id)
    subscription = await db.get(
        Subscription,
        subscription_id,
        options=[selectinload(Subscription.plan).load_only(Plan.duration_months)],
    )

    if not payment or not subscription:
        raise HTTPException(404)

    if payload["event"] == "payment.succeeded":
        payment.status = Status.COMPLETED

        today = datetime.date.today()
        subscription.start_date = today
        subscription.end_date = today + datetime.timedelta(
            30 * subscription.plan.duration_months
        )
        subscription.is_active = True
    elif payload["event"] == "payment.failed":
        payment.status = Status.FAILED

    await db.commit()
    return
