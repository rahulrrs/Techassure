from io import BytesIO

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import Finding, RiskScore


def generate_audit_report(db: Session) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER
    y = height - 54

    enterprise = db.scalar(select(RiskScore).where(RiskScore.scope == "enterprise").order_by(RiskScore.updated_at.desc()))
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(54, y, "TechAssure Executive IT Audit Report")
    y -= 34
    pdf.setFont("Helvetica", 11)
    pdf.drawString(54, y, f"Enterprise risk: {enterprise.score if enterprise else 0} ({enterprise.rating if enterprise else 'Not scored'})")
    y -= 28

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(54, y, "Findings")
    y -= 22
    pdf.setFont("Helvetica", 9)
    for finding in db.scalars(select(Finding).order_by(Finding.severity.desc()).limit(30)):
        if y < 72:
            pdf.showPage()
            y = height - 54
            pdf.setFont("Helvetica", 9)
        pdf.drawString(54, y, f"{finding.severity.value} | {finding.status.value} | {finding.title[:86]}")
        y -= 14
        pdf.drawString(72, y, f"Impact: {finding.impact[:100]}")
        y -= 14
        pdf.drawString(72, y, f"Remediation: {finding.remediation[:96]}")
        y -= 20

    pdf.save()
    buffer.seek(0)
    return buffer.read()
