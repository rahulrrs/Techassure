from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.domain import Evidence, User
from app.models.enums import Role
from app.schemas.common import EvidenceRead
from app.services.ingestion import ingest_dataset

router = APIRouter(prefix="/evidence", tags=["Evidence"], dependencies=[Depends(require_roles(Role.admin, Role.auditor))])


@router.get("", response_model=list[EvidenceRead])
def list_evidence(db: Session = Depends(get_db)) -> list[Evidence]:
    return list(db.scalars(select(Evidence).order_by(Evidence.created_at.desc()).limit(100)))


@router.post("/upload/{dataset_type}", response_model=EvidenceRead)
def upload(dataset_type: str, file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Evidence:
    try:
        return ingest_dataset(db, file, dataset_type, user.id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
