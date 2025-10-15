from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import settings

engine = create_async_engine(str(settings.postgres_dsn))
local_session = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with local_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]


class Base(AsyncAttrs, DeclarativeBase):
    pass
