from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import select

from app.core.db import SessionDep
from app.models.subscriptions import Subscription
from app.models.users import Role, User
from app.utils.fastapi_users import fastapi_users as fu

current_user = fu.current_user(active=True, verified=True)
CurrentUserDep = Annotated[User, Depends(current_user)]


def user_has_role(role: Role):
    async def dependency(cur_user: CurrentUserDep):
        if cur_user.role != role:
            raise HTTPException(403, detail="No permission")

    return dependency


async def user_has_active_subscription(db: SessionDep, cur_user: CurrentUserDep):
    sub = await db.scalar(
        select(Subscription).where(
            Subscription.user_id == cur_user.id, Subscription.is_active == True
        )
    )
    if not sub:
        raise HTTPException(403, "Active subscription required")


async def user_has_no_active_subscription(db: SessionDep, cur_user: CurrentUserDep):
    sub = await db.scalar(
        select(Subscription).where(
            Subscription.user_id == cur_user.id, Subscription.is_active == True
        )
    )
    if sub:
        raise HTTPException(400, "You already have active subscription")
