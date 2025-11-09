from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payments import Payment
from app.models.subscriptions import Plan
from app.models.users import User
from app.schemas.payments import PaymentRead

pytestmark = pytest.mark.asyncio


async def test_auth_required_to_access_payments(app: FastAPI, client: AsyncClient):
    res = await client.get(app.url_path_for("payments:list_payments"))
    assert res.status_code == 401


async def test_list_payments(
    app: FastAPI, auth_client: AsyncClient, db: AsyncSession, test_user: User
):
    db.add_all(
        [
            Payment(user=test_user, amount=9.99, currency="RUB"),
            Payment(user=test_user, amount=19.99, currency="RUB"),
        ]
    )
    await db.commit()

    res = await auth_client.get(app.url_path_for("payments:list_payments"))
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2


async def test_get_payment(
    app: FastAPI, auth_client: AsyncClient, db: AsyncSession, test_user: User
):
    payment = Payment(user=test_user, amount=9.99, currency="RUB")
    db.add(payment)
    await db.commit()
    await db.refresh(payment)

    res = await auth_client.get(app.url_path_for("payments:get_payment", id=payment.id))
    assert res.status_code == 200
    payment_data = PaymentRead.model_validate(res.json())
    assert payment_data.id == payment.id
    assert payment_data.amount == payment.amount
    assert payment_data.currency == payment.currency


@patch("app.api.v1.payments.yk.Payment.create")
async def test_buy_subscription(
    mock_yk_payment_create: MagicMock,
    app: FastAPI,
    auth_client: AsyncClient,
    basic_plan: Plan,
):
    mock_yk_confirmation = Mock(confirmation_url="http://pay.url/")
    mock_yk_payment = Mock(confirmation=mock_yk_confirmation)
    mock_yk_payment_create.return_value = mock_yk_payment

    res = await auth_client.post(
        app.url_path_for("payments:buy_subscription", plan_id=basic_plan.id),
        json={"return_url": "http://example.com"},
    )

    assert res.status_code == 200
    payment_data = res.json()
    assert payment_data["confirmation_url"] == mock_yk_confirmation.confirmation_url
