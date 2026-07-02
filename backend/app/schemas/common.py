from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str = Field(min_length=8)
    role: str = "Auditor"


class UserRead(ORMModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool


class EmployeeRead(ORMModel):
    id: int
    employee_id: str
    full_name: str
    department: str
    manager: str | None
    employment_status: str
    termination_date: date | None


class AccountRead(ORMModel):
    id: int
    username: str
    employee_id: str | None
    system_name: str
    is_active: bool
    mfa_enabled: bool
    privilege_level: str
    password_last_changed: date | None
    last_login: date | None


class AssetRead(ORMModel):
    id: int
    asset_tag: str
    hostname: str
    owner_employee_id: str | None
    department: str
    criticality: str
    patch_due_date: date | None
    last_patch_date: date | None


class ControlCreate(BaseModel):
    control_id: str
    name: str
    description: str
    test_type: str
    weight: float = Field(gt=0, default=1.0)
    frameworks: dict[str, list[str]] = Field(default_factory=dict)
    parameters: dict[str, Any] = Field(default_factory=dict)


class ControlRead(ControlCreate, ORMModel):
    id: int
    is_active: bool


class EvidenceRead(ORMModel):
    id: int
    filename: str
    dataset_type: str
    rows_loaded: int
    validation_summary: dict[str, Any]
    created_at: datetime


class TestResultRead(ORMModel):
    id: int
    control_id: int
    status: str
    population: int
    exceptions: int
    explanation: dict[str, Any]


class FindingCreate(BaseModel):
    title: str
    description: str
    severity: str = "Medium"
    department: str | None = None
    asset_tag: str | None = None
    owner: str | None = None
    impact: str
    remediation: str
    due_date: date | None = None


class FindingRead(FindingCreate, ORMModel):
    id: int
    status: str


class RiskScoreRead(ORMModel):
    id: int
    scope: str
    scope_value: str
    score: float
    rating: str
    explanation: dict[str, Any]


class DashboardSummary(BaseModel):
    kpis: dict[str, int | float]
    risk_trend: list[dict[str, Any]]
    department_risk: list[dict[str, Any]]
    severity_mix: list[dict[str, Any]]
    heatmap: list[dict[str, Any]]


class CopilotQuery(BaseModel):
    question: str


class CopilotAnswer(BaseModel):
    answer: str
    evidence: list[str]
    recommendations: list[str]
