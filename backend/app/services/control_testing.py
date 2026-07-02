from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import Account, Asset, Control, ControlTestResult, Employee, Finding
from app.models.enums import Severity


def seed_default_controls(db: Session) -> None:
    defaults = [
        ("IAM-001", "Terminated employees do not retain active accounts", "inactive_active_accounts", 3.0),
        ("IAM-002", "Privileged and active accounts require MFA", "missing_mfa", 2.5),
        ("IAM-003", "Admin privileges are limited to approved users", "excessive_admin", 2.0),
        ("IAM-004", "Passwords are rotated within policy", "stale_passwords", 1.5),
        ("VUL-001", "Critical assets are patched by due date", "overdue_patches", 3.0),
    ]
    for control_id, name, test_type, weight in defaults:
        if not db.scalar(select(Control).where(Control.control_id == control_id)):
            db.add(
                Control(
                    control_id=control_id,
                    name=name,
                    description=name,
                    test_type=test_type,
                    weight=weight,
                    frameworks={"ISO 27001": ["A.5", "A.8"], "NIST CSF": ["PR.AC", "PR.IP"], "SOC 2": ["CC6", "CC7"]},
                    parameters={"password_age_days": 90},
                )
            )
    db.commit()


def run_control(db: Session, control: Control) -> ControlTestResult:
    today = date.today()
    exceptions: list[dict] = []
    population = 0

    if control.test_type == "inactive_active_accounts":
        employees = {e.employee_id: e for e in db.scalars(select(Employee))}
        accounts = list(db.scalars(select(Account).where(Account.is_active.is_(True))))
        population = len(accounts)
        for account in accounts:
            employee = employees.get(account.employee_id or "")
            if employee and employee.employment_status.lower() != "active":
                exceptions.append({"username": account.username, "employee_id": account.employee_id, "reason": "Employee is not active"})
    elif control.test_type == "missing_mfa":
        accounts = list(db.scalars(select(Account).where(Account.is_active.is_(True))))
        population = len(accounts)
        for account in accounts:
            if not account.mfa_enabled and account.privilege_level.lower() in {"admin", "administrator", "privileged"}:
                exceptions.append({"username": account.username, "reason": "Privileged account has MFA disabled"})
    elif control.test_type == "excessive_admin":
        accounts = list(db.scalars(select(Account).where(Account.is_active.is_(True))))
        population = len(accounts)
        for account in accounts:
            if account.privilege_level.lower() in {"admin", "administrator", "domain admin", "superuser"}:
                exceptions.append({"username": account.username, "privilege": account.privilege_level})
    elif control.test_type == "stale_passwords":
        max_age = int(control.parameters.get("password_age_days", 90))
        accounts = list(db.scalars(select(Account).where(Account.is_active.is_(True))))
        population = len(accounts)
        for account in accounts:
            if not account.password_last_changed or account.password_last_changed < today - timedelta(days=max_age):
                exceptions.append({"username": account.username, "reason": f"Password age exceeds {max_age} days"})
    elif control.test_type == "overdue_patches":
        assets = list(db.scalars(select(Asset)))
        population = len(assets)
        for asset in assets:
            if asset.patch_due_date and asset.patch_due_date < today:
                exceptions.append({"asset_tag": asset.asset_tag, "hostname": asset.hostname, "department": asset.department})
    else:
        exceptions.append({"reason": f"No automated tester registered for {control.test_type}"})

    status = "Pass" if not exceptions else "Fail"
    result = ControlTestResult(
        control_id=control.id,
        status=status,
        population=population,
        exceptions=len(exceptions),
        explanation={"test_type": control.test_type, "sample_exceptions": exceptions[:25], "exception_rate": len(exceptions) / population if population else 0},
    )
    db.add(result)
    for item in exceptions[:20]:
        db.add(
            Finding(
                title=f"{control.control_id}: {control.name}",
                description=str(item),
                severity=Severity.high if control.weight >= 2.5 else Severity.medium,
                department=item.get("department"),
                asset_tag=item.get("asset_tag"),
                impact="Control failure increases IT risk and may weaken compliance posture.",
                remediation="Review the exception, assign an owner, and complete remediation evidence.",
                source_control_id=control.id,
            )
        )
    db.commit()
    db.refresh(result)
    return result


def run_all_controls(db: Session) -> list[ControlTestResult]:
    controls = list(db.scalars(select(Control).where(Control.is_active.is_(True))))
    return [run_control(db, control) for control in controls]
