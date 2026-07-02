from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.security import hash_password
from app.db.session import get_db
from app.models.domain import User
from app.models.enums import Role
from app.schemas.common import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["Users"], dependencies=[Depends(require_roles(Role.admin))])


@router.get("", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)) -> list[User]:
    return list(db.scalars(select(User).order_by(User.full_name)))


@router.post("", response_model=UserRead)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    user = User(email=payload.email, full_name=payload.full_name, hashed_password=hash_password(payload.password), role=Role(payload.role))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
