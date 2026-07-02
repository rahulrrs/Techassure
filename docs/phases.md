# Implementation Phases

## Phase 1: Database Schema And Backend APIs

Implemented SQLAlchemy entities for assets, employees, IAM accounts, controls, evidence, test results, findings, risk scores, and users. FastAPI exposes versioned APIs under `/api/v1`.

## Phase 2: Authentication And RBAC

JWT authentication supports Admin, Auditor, and Manager roles. Route dependencies enforce least-privilege access.

## Phase 3: Evidence Ingestion And Control Testing

CSV and Excel uploads load employee, account, and asset datasets. The automated testing engine detects terminated users with active accounts, missing MFA, excessive admin privileges, stale passwords, and overdue patches.

## Phase 4: Dashboards And Visualizations

React dashboard uses Recharts for department risk and severity analysis, with KPI cards and operational tables.

## Phase 5: AI Assistant And Report Generation

The audit copilot provides explainable, evidence-backed responses from stored findings and risk scores. PDF generation creates an executive audit report.

## Phase 6: Docker, Testing, Documentation, Deployment

Docker Compose runs PostgreSQL, FastAPI, and the React build. Tests cover security helpers and risk rating boundaries.
