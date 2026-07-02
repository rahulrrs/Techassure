from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.domain import User
from app.models.enums import Role
from app.schemas.common import LoginRequest, Token, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/bootstrap-admin", response_model=UserRead)
def bootstrap_admin(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    if db.scalar(select(User).where(User.role == Role.admin)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Admin already exists")
    user = User(email=payload.email, full_name=payload.full_name, hashed_password=hash_password(payload.password), role=Role.admin)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return Token(access_token=create_access_token(user.email, {"role": user.role.value}), role=user.role.value)
