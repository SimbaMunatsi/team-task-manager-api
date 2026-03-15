from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_id(db: Session, user_id: int) -> User | None:
    statement = select(User).where(User.id == user_id, User.deleted_at.is_(None))
    return db.execute(statement).scalar_one_or_none()


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email, User.deleted_at.is_(None))
    return db.execute(statement).scalar_one_or_none()


def get_user_by_username(db: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username, User.deleted_at.is_(None))
    return db.execute(statement).scalar_one_or_none()


def create_user(
    db: Session,
    *,
    username: str,
    email: str,
    hashed_password: str,
) -> User:
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user