from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import FindingStatus, Role, Severity


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.auditor)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Employee(Base, TimestampMixin):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    department: Mapped[str] = mapped_column(String(120), index=True)
    manager: Mapped[str | None] = mapped_column(String(255))
    employment_status: Mapped[str] = mapped_column(String(80), default="Active")
    termination_date: Mapped[date | None] = mapped_column(Date)


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_tag: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    hostname: Mapped[str] = mapped_column(String(255))
    owner_employee_id: Mapped[str | None] = mapped_column(String(80), index=True)
    department: Mapped[str] = mapped_column(String(120), index=True)
    criticality: Mapped[str] = mapped_column(String(50), default="Medium")
    patch_due_date: Mapped[date | None] = mapped_column(Date)
    last_patch_date: Mapped[date | None] = mapped_column(Date)


class Account(Base, TimestampMixin):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    employee_id: Mapped[str | None] = mapped_column(String(80), index=True)
    system_name: Mapped[str] = mapped_column(String(120), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    privilege_level: Mapped[str] = mapped_column(String(80), default="Standard")
    password_last_changed: Mapped[date | None] = mapped_column(Date)
    last_login: Mapped[date | None] = mapped_column(Date)


class Control(Base, TimestampMixin):
    __tablename__ = "controls"

    id: Mapped[int] = mapped_column(primary_key=True)
    control_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    test_type: Mapped[str] = mapped_column(String(100), index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    frameworks: Mapped[dict] = mapped_column(JSONB, default=dict)
    parameters: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Evidence(Base, TimestampMixin):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    dataset_type: Mapped[str] = mapped_column(String(80), index=True)
    rows_loaded: Mapped[int] = mapped_column(Integer, default=0)
    validation_summary: Mapped[dict] = mapped_column(JSONB, default=dict)
    uploaded_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))


class ControlTestResult(Base, TimestampMixin):
    __tablename__ = "control_test_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    control_id: Mapped[int] = mapped_column(ForeignKey("controls.id"), index=True)
    status: Mapped[str] = mapped_column(String(50))
    tested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    population: Mapped[int] = mapped_column(Integer, default=0)
    exceptions: Mapped[int] = mapped_column(Integer, default=0)
    explanation: Mapped[dict] = mapped_column(JSONB, default=dict)

    control: Mapped[Control] = relationship()


class Finding(Base, TimestampMixin):
    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    severity: Mapped[Severity] = mapped_column(Enum(Severity), default=Severity.medium)
    status: Mapped[FindingStatus] = mapped_column(Enum(FindingStatus), default=FindingStatus.open)
    department: Mapped[str | None] = mapped_column(String(120), index=True)
    asset_tag: Mapped[str | None] = mapped_column(String(80))
    owner: Mapped[str | None] = mapped_column(String(255))
    impact: Mapped[str] = mapped_column(Text)
    remediation: Mapped[str] = mapped_column(Text)
    due_date: Mapped[date | None] = mapped_column(Date)
    source_control_id: Mapped[int | None] = mapped_column(ForeignKey("controls.id"))


class RiskScore(Base, TimestampMixin):
    __tablename__ = "risk_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    scope: Mapped[str] = mapped_column(String(80), index=True)
    scope_value: Mapped[str] = mapped_column(String(120), index=True)
    score: Mapped[float] = mapped_column(Float)
    rating: Mapped[str] = mapped_column(String(50))
    explanation: Mapped[dict] = mapped_column(JSONB, default=dict)
