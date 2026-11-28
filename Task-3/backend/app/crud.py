"""Reusable async database operations. Routers call these; they never build queries themselves."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import schemas
from app.models import Note, User
from app.security import hash_password


class DuplicateEmailError(Exception):
    """Raised when a user with the same email already exists."""


# ---------- Users ----------
async def create_user(db: AsyncSession, data: schemas.UserCreate) -> User:
    user = User(
        username=data.username,
        email=data.email.lower(),
        password_hash=await hash_password(data.password),
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError as exc:
        # The UNIQUE constraint on users.email is the single source of truth (no race conditions).
        await db.rollback()
        raise DuplicateEmailError(data.email) from exc
    await db.refresh(user)
    return user


async def get_users(db: AsyncSession) -> Sequence[User]:
    result = await db.scalars(select(User).order_by(User.id))
    return result.all()


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def get_user_with_notes(db: AsyncSession, user_id: int) -> User | None:
    """Fetch a user and their notes with one extra SELECT (selectinload), not one per note."""
    stmt = select(User).options(selectinload(User.notes)).where(User.id == user_id)
    return (await db.execute(stmt)).scalar_one_or_none()


# ---------- Notes ----------
async def create_note(db: AsyncSession, data: schemas.NoteCreate) -> Note | None:
    """Create a note for a user. Returns None if that user does not exist."""
    if await db.get(User, data.user_id) is None:
        return None
    note = Note(title=data.title, content=data.content, user_id=data.user_id)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


async def get_notes(db: AsyncSession) -> Sequence[Note]:
    result = await db.scalars(select(Note).order_by(Note.id))
    return result.all()


async def get_note(db: AsyncSession, note_id: int) -> Note | None:
    return await db.get(Note, note_id)


async def get_notes_by_user(db: AsyncSession, user_id: int) -> Sequence[Note]:
    result = await db.scalars(
        select(Note).where(Note.user_id == user_id).order_by(Note.id)
    )
    return result.all()


async def update_note(
    db: AsyncSession, note_id: int, data: schemas.NoteUpdate
) -> Note | None:
    note = await db.get(Note, note_id)
    if note is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    await db.commit()
    await db.refresh(note)
    return note


async def delete_note(db: AsyncSession, note_id: int) -> bool:
    note = await db.get(Note, note_id)
    if note is None:
        return False
    await db.delete(note)
    await db.commit()
    return True
