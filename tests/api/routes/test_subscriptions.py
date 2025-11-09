import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscriptions import Plan, Subscription
from app.models.users import User
from app.schemas.subscriptions import PlanRead, SubscriptionRead

pytestmark = pytest.mark.asyncio


async def test_only_admin_creates_plan(app: FastAPI, auth_client: AsyncClient):
    res = await auth_client.post(app.url_path_for("subscriptions:create_plan"), json={})
    assert res.status_code == 403


async def test_only_admin_updates_plan(app: FastAPI, auth_client: AsyncClient):
    res = await auth_client.patch(
        app.url_path_for("subscriptions:update_plan", id=1), json={}
    )
    assert res.status_code == 403


async def test_list_plans(app: FastAPI, client: AsyncClient, db: AsyncSession):
    plan1 = Plan(
        title="Basic",
        description="Basic",
        duration_months=1,
        price=9.99,
        currency="RUB",
    )
    plan2 = Plan(
        title="Pro",
        description="Pro",
        duration_months=6,
        price=49.99,
        currency="RUB",
    )
    db.add_all([plan1, plan2])
    await db.commit()

    res = await client.get(app.url_path_for("subscriptions:list_plans"))
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2


async def test_get_plan(app: FastAPI, client: AsyncClient, db: AsyncSession):
    plan = Plan(
        title="Basic",
        description="Basic",
        duration_months=1,
        price=9.99,
        currency="RUB",
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)

    res = await client.get(app.url_path_for("subscriptions:get_plan", id=plan.id))
    assert res.status_code == 200
    plan_data = PlanRead.model_validate(res.json())
    assert plan_data.id == plan.id


async def test_get_subscription(
    app: FastAPI,
    auth_client: AsyncClient,
    db: AsyncSession,
    test_user: User,
    basic_plan: Plan,
):
    sub = Subscription(user=test_user, plan=basic_plan)
    db.add(sub)
    await db.commit()
    await db.refresh(sub)

    res = await auth_client.get(
        app.url_path_for("subscriptions:get_subscription", id=sub.id)
    )
    assert res.status_code == 200
    sub_data = SubscriptionRead.model_validate(res.json())
    assert sub_data.id == sub.id
    assert sub_data.user_id == test_user.id
    assert sub_data.plan_id == basic_plan.id


async def test_list_subscriptions(
    app: FastAPI,
    auth_client: AsyncClient,
    db: AsyncSession,
    test_user: User,
    basic_plan: Plan,
):
    db.add_all(
        [
            Subscription(user=test_user, plan=basic_plan),
            Subscription(user=test_user, plan=basic_plan),
        ]
    )
    await db.commit()

    res = await auth_client.get(app.url_path_for("subscriptions:list_subscriptions"))
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2


async def test_cancel_subscription(
    app: FastAPI,
    auth_client: AsyncClient,
    db: AsyncSession,
    test_user: User,
    basic_plan: Plan,
):
    sub = Subscription(user=test_user, plan=basic_plan, is_active=True)
    db.add(sub)
    await db.commit()
    await db.refresh(sub)

    res = await auth_client.post(
        app.url_path_for("subscriptions:cancel_subscription", id=sub.id)
    )
    assert res.status_code == 200
    await db.refresh(sub)
    assert sub.is_active is False
