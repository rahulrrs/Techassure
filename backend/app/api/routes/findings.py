from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.domain import Finding
from app.models.enums import FindingStatus, Role
from app.schemas.common import FindingCreate, FindingRead

router = APIRouter(prefix="/findings", tags=["Findings"], dependencies=[Depends(require_roles(Role.admin, Role.auditor, Role.manager))])


@router.get("", response_model=list[FindingRead])
def list_findings(db: Session = Depends(get_db)) -> list[Finding]:
    return list(db.scalars(select(Finding).order_by(Finding.created_at.desc()).limit(300)))


@router.post("", response_model=FindingRead)
def create_finding(payload: FindingCreate, db: Session = Depends(get_db)) -> Finding:
    finding = Finding(**payload.model_dump())
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding


@router.patch("/{finding_id}/status/{status}", response_model=FindingRead)
def update_status(finding_id: int, status: FindingStatus, db: Session = Depends(get_db)) -> Finding:
    finding = db.get(Finding, finding_id)
    finding.status = status
    db.commit()
    db.refresh(finding)
    return finding
