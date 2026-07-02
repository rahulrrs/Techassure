from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.domain import Asset, Control, ControlTestResult, Finding, RiskScore
from app.models.enums import FindingStatus


def _rating(score: float) -> str:
    if score >= 75:
        return "Critical"
    if score >= 50:
        return "High"
    if score >= 25:
        return "Medium"
    return "Low"


def recompute_risk_scores(db: Session) -> list[RiskScore]:
    db.query(RiskScore).delete()
    latest_results = []
    seen_controls = set()
    for result in db.scalars(select(ControlTestResult).order_by(ControlTestResult.tested_at.desc())):
        if result.control_id not in seen_controls:
            latest_results.append(result)
            seen_controls.add(result.control_id)

    controls = {c.id: c for c in db.scalars(select(Control))}
    weighted = []
    for result in latest_results:
        control = controls.get(result.control_id)
        if not control or not result.population:
            continue
        exception_rate = result.exceptions / result.population
        weighted.append((control.weight, exception_rate, control.control_id))
    total_weight = sum(item[0] for item in weighted) or 1
    score = round(sum(weight * rate * 100 for weight, rate, _ in weighted) / total_weight, 2)
    enterprise = RiskScore(
        scope="enterprise",
        scope_value="All",
        score=score,
        rating=_rating(score),
        explanation={"drivers": [{"control": cid, "weight": weight, "exception_rate": rate} for weight, rate, cid in weighted]},
    )
    db.add(enterprise)

    departments = defaultdict(lambda: {"findings": 0, "critical_high": 0})
    for finding in db.scalars(select(Finding).where(Finding.status != FindingStatus.remediated)):
        key = finding.department or "Unassigned"
        departments[key]["findings"] += 1
        if finding.severity.value in {"Critical", "High"}:
            departments[key]["critical_high"] += 1
    for department, data in departments.items():
        dept_score = min(100, data["findings"] * 8 + data["critical_high"] * 12)
        db.add(RiskScore(scope="department", scope_value=department, score=dept_score, rating=_rating(dept_score), explanation=data))
    db.commit()
    return list(db.scalars(select(RiskScore)))


def dashboard_summary(db: Session) -> dict:
    kpis = {
        "assets": db.scalar(select(func.count()).select_from(Asset)) or 0,
        "open_findings": db.scalar(select(func.count()).select_from(Finding).where(Finding.status == FindingStatus.open)) or 0,
        "controls": db.scalar(select(func.count()).select_from(Control)) or 0,
        "enterprise_risk": db.scalar(select(RiskScore.score).where(RiskScore.scope == "enterprise").order_by(RiskScore.updated_at.desc())) or 0,
    }
    department_risk = [
        {"department": r.scope_value, "score": r.score, "rating": r.rating}
        for r in db.scalars(select(RiskScore).where(RiskScore.scope == "department").order_by(RiskScore.score.desc()))
    ]
    severity_rows = db.execute(select(Finding.severity, func.count(Finding.id)).group_by(Finding.severity)).all()
    return {
        "kpis": kpis,
        "risk_trend": [{"period": "Current", "score": kpis["enterprise_risk"]}],
        "department_risk": department_risk,
        "severity_mix": [{"severity": str(sev.value), "count": count} for sev, count in severity_rows],
        "heatmap": [{"framework": "ISO 27001", "domain": "Access Control", "risk": kpis["enterprise_risk"]}],
    }
