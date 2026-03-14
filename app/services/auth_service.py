from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
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