"""
Create the initial admin account.

Usage (Windows, venv active):
    python create_admin.py <username> <email> <password>

The script is idempotent: if the username already exists, it will not
overwrite the existing record; instead it promotes the existing user to admin.
"""

import sys

from database import Base, SessionLocal, engine
import models  # noqa: F401  (ensures models are registered on Base)
from models import User
from security import get_password_hash


def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: python create_admin.py <username> <email> <password>")
        sys.exit(1)

    username, email, password = sys.argv[1], sys.argv[2], sys.argv[3]

    if len(password) < 6:
        print("Password must be at least 6 characters.")
        sys.exit(1)

    # Ensure tables exist (in case this runs before main.py).
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            existing.role = "admin"
            existing.is_active = True
            db.commit()
            print(f"User '{username}' already existed — promoted to admin.")
            return

        admin = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print(f"Admin '{username}' created successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
