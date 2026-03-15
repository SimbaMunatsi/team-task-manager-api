from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.crud.user import create_user, get_user_by_email, get_user_by_username
from app.models.user import User
from app.schemas.auth import RegisterRequest


def register_user(db: Session, user_in: RegisterRequest) -> User:
    existing_email = get_user_by_email(db, user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )

    existing_username = get_user_by_username(db, user_in.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken.",
        )

    hashed_password = hash_password(user_in.password)

    user = create_user(
        db,
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
    )
    return user


def authenticate_user(db: Session, email: str, password: str) -> str:
    user = get_user_by_email(db, email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user.",
        )

    access_token = create_access_token(subject=user.id)
    return access_token