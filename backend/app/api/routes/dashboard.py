from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.domain import RiskScore
from app.models.enums import Role
from app.schemas.common import CopilotAnswer, CopilotQuery, DashboardSummary, RiskScoreRead
from app.services.copilot import answer_audit_question
from app.services.reports import generate_audit_report
from app.services.risk import dashboard_summary, recompute_risk_scores

router = APIRouter(prefix="/dashboard", tags=["Dashboard"], dependencies=[Depends(require_roles(Role.admin, Role.auditor, Role.manager))])


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db)) -> dict:
    return dashboard_summary(db)


@router.post("/risk/recompute", response_model=list[RiskScoreRead])
def recompute(db: Session = Depends(get_db)) -> list[RiskScore]:
    return recompute_risk_scores(db)


@router.get("/risk", response_model=list[RiskScoreRead])
def risk_scores(db: Session = Depends(get_db)) -> list[RiskScore]:
    return list(db.scalars(select(RiskScore).order_by(RiskScore.scope, RiskScore.score.desc())))


@router.post("/copilot", response_model=CopilotAnswer)
def copilot(payload: CopilotQuery, db: Session = Depends(get_db)) -> dict:
    return answer_audit_question(db, payload.question)


@router.get("/report.pdf")
def report(db: Session = Depends(get_db)) -> Response:
    return Response(generate_audit_report(db), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=techassure-audit-report.pdf"})
