import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscriptions import Plan

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
    data = res.json()
    assert data["id"] == plan.id
