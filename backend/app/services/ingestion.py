from datetime import date
from io import BytesIO
from typing import Any

import pandas as pd
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.domain import Account, Asset, Employee, Evidence


DATASET_COLUMNS = {
    "employees": {"employee_id", "full_name", "department", "employment_status"},
    "accounts": {"username", "system_name", "is_active", "mfa_enabled", "privilege_level"},
    "assets": {"asset_tag", "hostname", "department", "criticality"},
}


def _parse_date(value: Any) -> date | None:
    if value is None or pd.isna(value) or value == "":
        return None
    return pd.to_datetime(value).date()


def _read_upload(file: UploadFile) -> pd.DataFrame:
    content = file.file.read()
    if file.filename.lower().endswith(".csv"):
        return pd.read_csv(BytesIO(content))
    if file.filename.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(BytesIO(content))
    raise ValueError("Only CSV and Excel files are supported")


def ingest_dataset(db: Session, file: UploadFile, dataset_type: str, uploaded_by_id: int | None) -> Evidence:
    if dataset_type not in DATASET_COLUMNS:
        raise ValueError(f"Unsupported dataset type: {dataset_type}")
    frame = _read_upload(file)
    frame.columns = [str(column).strip() for column in frame.columns]
    missing = sorted(DATASET_COLUMNS[dataset_type] - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    rows_loaded = 0
    for record in frame.fillna("").to_dict(orient="records"):
        if dataset_type == "employees":
            obj = db.query(Employee).filter(Employee.employee_id == str(record["employee_id"])).one_or_none() or Employee(employee_id=str(record["employee_id"]))
            obj.full_name = str(record["full_name"])
            obj.department = str(record["department"])
            obj.manager = str(record.get("manager") or "")
            obj.employment_status = str(record.get("employment_status") or "Active")
            obj.termination_date = _parse_date(record.get("termination_date"))
        elif dataset_type == "accounts":
            obj = db.query(Account).filter(Account.username == str(record["username"])).one_or_none() or Account(username=str(record["username"]))
            obj.employee_id = str(record.get("employee_id") or "")
            obj.system_name = str(record["system_name"])
            obj.is_active = str(record.get("is_active")).lower() in {"true", "1", "yes", "active"}
            obj.mfa_enabled = str(record.get("mfa_enabled")).lower() in {"true", "1", "yes"}
            obj.privilege_level = str(record.get("privilege_level") or "Standard")
            obj.password_last_changed = _parse_date(record.get("password_last_changed"))
            obj.last_login = _parse_date(record.get("last_login"))
        else:
            obj = db.query(Asset).filter(Asset.asset_tag == str(record["asset_tag"])).one_or_none() or Asset(asset_tag=str(record["asset_tag"]))
            obj.hostname = str(record["hostname"])
            obj.owner_employee_id = str(record.get("owner_employee_id") or "")
            obj.department = str(record["department"])
            obj.criticality = str(record.get("criticality") or "Medium")
            obj.patch_due_date = _parse_date(record.get("patch_due_date"))
            obj.last_patch_date = _parse_date(record.get("last_patch_date"))
        db.add(obj)
        rows_loaded += 1

    evidence = Evidence(
        filename=file.filename,
        dataset_type=dataset_type,
        rows_loaded=rows_loaded,
        validation_summary={"required_columns": sorted(DATASET_COLUMNS[dataset_type]), "missing_columns": missing},
        uploaded_by_id=uploaded_by_id,
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence
