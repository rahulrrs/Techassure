from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.domain import Account, Asset, Employee
from app.models.enums import Role
from app.schemas.common import AccountRead, AssetRead, EmployeeRead

router = APIRouter(prefix="/inventory", tags=["Inventory"], dependencies=[Depends(require_roles(Role.admin, Role.auditor, Role.manager))])


@router.get("/employees", response_model=list[EmployeeRead])
def employees(db: Session = Depends(get_db)) -> list[Employee]:
    return list(db.scalars(select(Employee).order_by(Employee.department, Employee.full_name).limit(500)))


@router.get("/accounts", response_model=list[AccountRead])
def accounts(db: Session = Depends(get_db)) -> list[Account]:
    return list(db.scalars(select(Account).order_by(Account.system_name, Account.username).limit(500)))


@router.get("/assets", response_model=list[AssetRead])
def assets(db: Session = Depends(get_db)) -> list[Asset]:
    return list(db.scalars(select(Asset).order_by(Asset.department, Asset.hostname).limit(500)))
