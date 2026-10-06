"""Lean user auth: default-admin seeding and email/password verification."""
import os
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.db.models.user import User

# Dev/first-run convenience only. Override via env vars for anything beyond
# local development -- do not rely on the fallback password.
DEFAULT_ADMIN_EMAIL = os.environ.get("DEFAULT_ADMIN_EMAIL", "admin@example.com")
DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD", "change-me-immediately")


def ensure_default_admin(db: Session) -> None:
    """Seeds one default admin user if the users table is empty."""
    if db.query(User).first() is not None:
        return
    admin = User(
        email=DEFAULT_ADMIN_EMAIL,
        hashed_password=hash_password(DEFAULT_ADMIN_PASSWORD),
        is_active=True,
        is_admin=True,
    )
    db.add(admin)
    db.commit()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def register_user(db: Session, email: str, password: str) -> User:
    """Creates a new, non-admin user. Caller is responsible for checking the
    email isn't already taken (see app/api/v1/auth.py) before calling this."""
    user = User(
        email=email,
        hashed_password=hash_password(password),
        is_active=True,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
