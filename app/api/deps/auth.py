from typing import Annotated

from fastapi import Depends, HTTPException

from app.models.users import Role, User
from app.utils.fastapi_users import fastapi_users as fu

current_user = fu.current_user(active=True)
CurrentUserDep = Annotated[User, Depends(current_user)]


def user_has_role(role: Role):
    async def dependency(cur_user: CurrentUserDep):
        if cur_user.role != role:
            raise HTTPException(403, detail="No permission")

    return dependency
