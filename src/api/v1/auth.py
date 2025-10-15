from fastapi import APIRouter

from src.schemas.users import UserCreate, UserRead
from src.utils.fastapi_users import auth_backend
from src.utils.fastapi_users import fastapi_users as fu

router = APIRouter(prefix="/auth", tags=["auth"])

router.include_router(fu.get_auth_router(auth_backend))
router.include_router(fu.get_register_router(UserRead, UserCreate))
router.include_router(fu.get_reset_password_router())
router.include_router(fu.get_verify_router(UserRead))
