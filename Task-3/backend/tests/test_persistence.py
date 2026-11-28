"""Persistence and relational-integrity tests.

Each test talks to the API, then opens a brand-new engine and session on the
same SQLite file, which is the same situation as a server restart."""

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload

from app.database import create_db_engine
from app.models import Note, User
from app.security import verify_password


async def test_committed_data_survives_a_new_session(client, db_url, make_user, make_note):
    user = await make_user(username="persist", email="persist@example.com")
    await make_note(user["id"], title="Kept 1")
    await make_note(user["id"], title="Kept 2")

    new_engine = create_db_engine(db_url)  # a completely fresh connection to the file
    try:
        async with async_sessionmaker(new_engine)() as session:
            stored = (
                await session.execute(
                    select(User).options(selectinload(User.notes)).where(User.email == "persist@example.com")
                )
            ).scalar_one()
            assert stored.username == "persist"
            assert [n.title for n in stored.notes] == ["Kept 1", "Kept 2"]
    finally:
        await new_engine.dispose()


async def test_update_and_delete_are_persisted(client, db_url, make_user, make_note):
    user = await make_user()
    keep = await make_note(user["id"], title="Before")
    gone = await make_note(user["id"], title="Delete me")
    await client.put(f"/notes/{keep['id']}", json={"title": "After"})
    await client.delete(f"/notes/{gone['id']}")

    new_engine = create_db_engine(db_url)
    try:
        async with async_sessionmaker(new_engine)() as session:
            titles = (await session.scalars(select(Note.title))).all()
            assert titles == ["After"]
    finally:
        await new_engine.dispose()


async def test_password_is_stored_as_a_hash(client, db_url, make_user):
    await make_user(email="hash@example.com", password="MySecret123")
    new_engine = create_db_engine(db_url)
    try:
        async with async_sessionmaker(new_engine)() as session:
            stored = (await session.scalars(select(User))).one()
            assert stored.password_hash != "MySecret123"
            assert stored.password_hash.startswith("$argon2")
            assert verify_password("MySecret123", stored.password_hash)
            assert not verify_password("WrongPassword", stored.password_hash)
    finally:
        await new_engine.dispose()


async def test_database_rejects_note_with_unknown_user(engine):
    """Foreign keys are enforced by SQLite itself, not just by the API layer."""
    async with async_sessionmaker(engine)() as session:
        session.add(Note(title="Orphan", content="", user_id=12345))
        with pytest.raises(IntegrityError):
            await session.commit()


async def test_deleting_a_user_cascades_to_their_notes(client, engine, make_user, make_note):
    doomed = await make_user()
    survivor = await make_user()
    await make_note(doomed["id"], title="Goes away 1")
    await make_note(doomed["id"], title="Goes away 2")
    await make_note(survivor["id"], title="Stays")

    async with async_sessionmaker(engine)() as session:
        await session.delete(await session.get(User, doomed["id"]))
        await session.commit()

    async with async_sessionmaker(engine)() as session:
        assert await session.scalar(select(func.count()).select_from(User)) == 1
        assert (await session.scalars(select(Note.title))).all() == ["Stays"]
