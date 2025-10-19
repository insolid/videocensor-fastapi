from fastapi import APIRouter

from app.schemas.users import UserRead, UserUpdate
from app.utils.fastapi_users import fastapi_users as fu

router = APIRouter(prefix="/users", tags=["users"])

router.include_router(fu.get_users_router(UserRead, UserUpdate))
