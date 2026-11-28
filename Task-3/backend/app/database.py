"""Async SQLAlchemy engine, session factory and the get_db dependency."""

import os
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

# The database file lives in backend/ no matter which folder the server is started from.
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv(
    "DATABASE_URL", f"sqlite+aiosqlite:///{(BASE_DIR / 'notes.db').as_posix()}"
)


class Base(DeclarativeBase):
    """Parent class of all ORM models."""


def create_db_engine(url: str) -> AsyncEngine:
    """Create an async engine that enforces SQLite foreign keys on every connection."""
    engine = create_async_engine(url)

    @event.listens_for(engine.sync_engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record) -> None:
        # SQLite ignores FOREIGN KEY constraints unless this pragma is switched on.
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


engine = create_db_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Give each request its own session and always close it afterwards."""
    async with AsyncSessionLocal() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db)]


async def init_db() -> None:
    """Create missing tables on startup.

    create_all() only creates tables that do not exist yet. It never alters or
    drops existing tables, so existing data is kept across restarts, but it also
    cannot apply later schema changes (new columns, renamed fields). For that,
    use a migration tool such as Alembic (see the README).
    """
    from app import models  # noqa: F401  (importing registers the tables on Base)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
