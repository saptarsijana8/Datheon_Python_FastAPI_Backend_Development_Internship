"""Shared fixtures. Every test gets its own temporary SQLite file, so tests are
isolated and the development database (notes.db) is never touched."""

from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.database import Base, create_db_engine, get_db
from app.main import app

JsonDict = dict[str, Any]


@pytest_asyncio.fixture
async def db_url(tmp_path) -> str:
    return f"sqlite+aiosqlite:///{(tmp_path / 'test.db').as_posix()}"


@pytest_asyncio.fixture
async def engine(db_url: str) -> AsyncGenerator[AsyncEngine, None]:
    test_engine = create_db_engine(db_url)
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture
async def client(engine: AsyncEngine) -> AsyncGenerator[AsyncClient, None]:
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def make_user(client: AsyncClient) -> Callable[..., Awaitable[JsonDict]]:
    """Factory: create a user through the API and return the response JSON."""
    counter = 0

    async def _make_user(**overrides: Any) -> JsonDict:
        nonlocal counter
        counter += 1
        payload = {
            "username": f"user{counter}",
            "email": f"user{counter}@example.com",
            "password": "StrongPass123",
        } | overrides
        response = await client.post("/users/", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make_user


@pytest_asyncio.fixture
async def make_note(client: AsyncClient) -> Callable[..., Awaitable[JsonDict]]:
    """Factory: create a note through the API and return the response JSON."""

    async def _make_note(user_id: int, **overrides: Any) -> JsonDict:
        payload = {"title": "A note", "content": "Some content", "user_id": user_id} | overrides
        response = await client.post("/notes/", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make_note
