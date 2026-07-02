from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.domain import Control, ControlTestResult
from app.models.enums import Role
from app.schemas.common import ControlCreate, ControlRead, TestResultRead
from app.services.control_testing import run_all_controls, run_control, seed_default_controls

router = APIRouter(prefix="/controls", tags=["Controls"], dependencies=[Depends(require_roles(Role.admin, Role.auditor))])


@router.post("/seed", response_model=dict)
def seed(db: Session = Depends(get_db)) -> dict:
    seed_default_controls(db)
    return {"status": "seeded"}


@router.get("", response_model=list[ControlRead])
def list_controls(db: Session = Depends(get_db)) -> list[Control]:
    return list(db.scalars(select(Control).order_by(Control.control_id)))


@router.post("", response_model=ControlRead)
def create_control(payload: ControlCreate, db: Session = Depends(get_db)) -> Control:
    control = Control(**payload.model_dump())
    db.add(control)
    db.commit()
    db.refresh(control)
    return control


@router.post("/{control_id}/run", response_model=TestResultRead)
def run_one(control_id: int, db: Session = Depends(get_db)) -> ControlTestResult:
    return run_control(db, db.get(Control, control_id))


@router.post("/run-all", response_model=list[TestResultRead])
def run_all(db: Session = Depends(get_db)) -> list[ControlTestResult]:
    return run_all_controls(db)
