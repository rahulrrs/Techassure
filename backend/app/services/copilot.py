from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import Finding, RiskScore


def answer_audit_question(db: Session, question: str) -> dict:
    risk = db.scalar(select(RiskScore).where(RiskScore.scope == "enterprise").order_by(RiskScore.updated_at.desc()))
    findings = list(db.scalars(select(Finding).order_by(Finding.created_at.desc()).limit(8)))
    evidence = [f"{item.severity.value} finding: {item.title}" for item in findings]
    recommendations = [
        "Prioritize remediation for high-severity access and patch exceptions.",
        "Require evidence owners to attach remediation proof before closing findings.",
        "Re-run automated controls after each data refresh to confirm residual risk.",
    ]
    answer = (
        f"Based on current TechAssure evidence, enterprise risk is {risk.score if risk else 0} "
        f"({risk.rating if risk else 'Not scored'}). The most relevant open issues are "
        f"{', '.join(evidence[:3]) if evidence else 'not yet available'}. "
        "This response is explainable from stored findings and risk-score drivers; configure an LLM key to enrich the narrative."
    )
    if "mfa" in question.lower():
        answer += " MFA-related exceptions should be treated as priority identity risk because they increase account takeover exposure."
    return {"answer": answer, "evidence": evidence, "recommendations": recommendations}
