from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps.auth import CurrentUserDep, user_has_role
from app.core.db import SessionDep
from app.models.subscriptions import Plan, Subscription
from app.models.users import Role
from app.schemas.subscriptions import (
    PlanCreate,
    PlanQuery,
    PlanRead,
    PlanUpdate,
    SubscriptionCreate,
    SubscriptionRead,
)
from app.utils.db import exists_or_error
from app.utils.fastcrud import CustomFastCRUD

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
plan_crud = CustomFastCRUD(model=Plan, updated_at_column="")
subscription_crud = CustomFastCRUD(model=Subscription)


# =============== Plans ===============


@router.get("/plans/{id}", response_model=PlanRead, name="subscriptions:get_plan")
async def get_plan(db: SessionDep, id: int):
    return await plan_crud.get(db, id=id)


@router.get("/plans", response_model=list[PlanRead], name="subscriptions:list_plans")
async def list_plans(db: SessionDep, q: Annotated[PlanQuery, Query()]):
    return await plan_crud.get_multi(db, **q.model_dump())


@router.post(
    "/plans",
    response_model=PlanRead,
    name="subscriptions:create_plan",
    dependencies=[Depends(user_has_role(role=Role.ADMIN))],
)
async def create_plan(db: SessionDep, plan: PlanCreate):
    return await plan_crud.create(db, plan)


@router.patch(
    "/plans/{id}",
    response_model=PlanRead,
    name="subscriptions:update_plan",
    dependencies=[Depends(user_has_role(role=Role.ADMIN))],
)
async def update_plan(db: SessionDep, id: int, plan: PlanUpdate):
    return await plan_crud.update(
        db=db,
        object=plan,
        schema_to_select=PlanRead,
        id=id,
    )


@router.delete(
    "/plans/{id}",
    response_model=None,
    name="subscriptions:delete_plan",
    dependencies=[Depends(user_has_role(role=Role.ADMIN))],
)
async def delete_plan(db: SessionDep, id: int):
    return await plan_crud.delete(db, id=id)


# =============== Subscriptions ===============


@router.get(
    "/{id}",
    response_model=SubscriptionRead,
    name="subscriptions:get_subscription",
)
async def get_subscription(db: SessionDep, id: int, cur_user: CurrentUserDep):
    return await subscription_crud.get(db, id=id, user_id=cur_user.id)


@router.get(
    "/",
    response_model=list[SubscriptionRead],
    name="subscriptions:list_subscriptions",
)
async def list_subscriptions(db: SessionDep, cur_user: CurrentUserDep):
    return await subscription_crud.get_multi(db, user_id=cur_user.id)


@router.post(
    "/", response_model=SubscriptionRead, name="subscriptions:create_subscription"
)
async def create_subscription(
    db: SessionDep,
    subscription: SubscriptionCreate,
    cur_user: CurrentUserDep,
):
    await exists_or_error(db, Plan.id, subscription.plan_id)
    sub = Subscription(**subscription.model_dump(), user_id=cur_user.id)
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return sub


@router.post(
    "/{id}/cancel",
    name="subscriptions:cancel_subscription",
    response_model=dict[str, str],
)
async def cancel_subscription(db: SessionDep, id: int, cur_user: CurrentUserDep):
    sub = await subscription_crud.get(db, id=id, user_id=cur_user.id)
    subscription = await db.get(Subscription, sub["id"])
    subscription.is_active = False  # type: ignore
    await db.commit()
    return {"detail": "Subscription cancelled successfully"}
