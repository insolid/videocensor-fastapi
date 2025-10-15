from fastapi import APIRouter

from src.schemas.users import UserRead, UserUpdate
from src.utils.fastapi_users import fastapi_users as fu

router = APIRouter(prefix="/users", tags=["users"])

router.include_router(fu.get_users_router(UserRead, UserUpdate))
