from collections.abc import AsyncGenerator

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.db import get_db
from app.main import app as application
from app.models.base import Base
from app.models.users import User
from app.utils.fastapi_users import get_jwt_strategy

# TEST_DB_URL = "sqlite+aiosqlite:///test_db.db"
TEST_DB_URL = "sqlite+aiosqlite://"

engine = create_async_engine(TEST_DB_URL)
local_session = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with local_session() as session:
        yield session


application.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async for session in override_get_db():
        yield session


@pytest_asyncio.fixture(scope="session")
async def app() -> FastAPI:
    return application


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> User:
    user = User(email="test@example.com", hashed_password="password", is_verified=True)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_client(test_user: User, client: AsyncClient) -> AsyncClient:
    token = await get_jwt_strategy().write_token(test_user)
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
