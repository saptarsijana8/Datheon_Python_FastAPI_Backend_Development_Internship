"""Password hashing with Argon2 (plaintext passwords are never stored)."""

import asyncio

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

_hasher = PasswordHasher()


async def hash_password(password: str) -> str:
    """Hash in a worker thread so the slow, CPU-heavy hashing doesn't block the event loop."""
    return await asyncio.to_thread(_hasher.hash, password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHashError):
        return False
