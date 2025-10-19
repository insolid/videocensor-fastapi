import re

from fastapi import Depends, HTTPException, Request
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

SECRET = "SECRET"


async def get_user_db(session: SessionDep):
    yield SQLAlchemyUserDatabase(session, User)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Request | None = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        # Send to email a frontend endpoint for email confirmation with token like this:
        # http://frontend/email/confirm/CjP8DXvZPnwgTo5Pe072Jp6m0M
        # And then frontend extracts that token and resends to server
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def validate_password(self, password: str, *args, **kwargs):
        errors = {}

        if len(password) < 6:
            errors["length"] = "Password must be at least 6 characters long"
        if not re.search(r"[A-Z]", password):
            errors["uppercase"] = "Password must contain at least one uppercase letter"
        if not re.search(r"[a-z]", password):
            errors["lowercase"] = "Password must contain at least one lowercase letter"
        if not re.search(r"[0-9]", password):
            errors["number"] = "Password must contain at least one number"
        if not re.search(r"[!@#$%^&*()]", password):
            errors["special_chars"] = (
                "Password must contain at least one special character"
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
        secret=settings.jwt_secret_key, lifetime_seconds=settings.jwt_expire_minutes
    )


auth_backend = AuthenticationBackend(
    name="jwt", transport=bearer_transport, get_strategy=get_jwt_strategy
)
fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
