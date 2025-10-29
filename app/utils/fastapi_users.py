import re

from fastapi import Depends, HTTPException
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from app.core.config import settings
from app.core.db import SessionDep
from app.models.users import User

from .emails import send_email

SECRET = "SECRET"


async def get_user_db(session: SessionDep):
    yield SQLAlchemyUserDatabase(session, User)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_forgot_password(self, user: User, token: str, *args, **kwargs):
        await send_email(
            user.email,
            "Forgot password",
            f"https://frontend.org/forgot-password/{token}",
        )

    async def on_after_request_verify(self, user: User, token: str, *args, **kwargs):
        # Send to email a frontend endpoint for email confirmation with token like this:
        # http://frontend/confirm-email/CjP8DXvZPnwgTo5Pe072Jp6m0M
        # And then frontend extracts that token and resends to server
        await send_email(
            user.email,
            "Verify email",
            f"https://frontend.org/confirm-email/{token}",
        )

    async def validate_password(self, password: str, *args, **kwargs):
        errors = {}

        if len(password) < 6:
            errors["length"] = "At least 6 chars required"
        if not re.search(r"[A-Z]", password):
            errors["uppercase"] = "At least one uppercase letter required"
        if not re.search(r"[a-z]", password):
            errors["lowercase"] = "At least one lowercase letter required"
        if not re.search(r"[0-9]", password):
            errors["number"] = "At least one number required"
        special_chars = "!@#$%^&*()"
        if not re.search(rf"[{special_chars}]", password):
            errors["special_chars"] = (
                f"At least one of special characters required: {special_chars}"
            )

        if errors:
            raise HTTPException(status_code=400, detail=errors)
        else:
            return


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.jwt_secret_key,
        lifetime_seconds=settings.jwt_expire_minutes * 60,
    )


auth_backend = AuthenticationBackend(
    name="jwt", transport=bearer_transport, get_strategy=get_jwt_strategy
)
fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
