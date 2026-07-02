# TechAssure

TechAssure is a full-stack demonstration GRC platform for IT audit workflows, control testing, continuous compliance monitoring, explainable risk scoring, AI-assisted audit analysis, and executive reporting.

## Stack

- Frontend: React, TypeScript, Tailwind CSS, Recharts
- Backend: FastAPI, SQLAlchemy, JWT RBAC
- Database: PostgreSQL
- Uploads: CSV and Excel for employees, accounts, and assets
- Reports: PDF executive audit report
- Deployment: Docker Compose

## Quick Start

```bash
docker compose up --build
```

Open:

- Frontend: http://localhost:8080
- API docs: http://localhost:8000/docs

The frontend bootstraps a demo admin account on first load:

- Email: `admin@techassure.local`
- Password: `ChangeMe123!`

## Demo Flow

1. Start the stack.
2. Upload sample CSVs from `samples/` through the API docs:
   - `POST /api/v1/evidence/upload/employees`
   - `POST /api/v1/evidence/upload/accounts`
   - `POST /api/v1/evidence/upload/assets`
3. In the frontend, click `Run Controls`.
4. Review dashboard KPIs, department risk, findings, evidence loads, and AI Copilot output.
5. Download the executive PDF from `GET /api/v1/dashboard/report.pdf`.

## Architecture

The backend follows a modular service layout:

- `models`: SQLAlchemy domain schema
- `schemas`: Pydantic request and response models
- `api/routes`: versioned FastAPI endpoints
- `services`: ingestion, control testing, risk scoring, copilot, reporting
- `repositories`: base repository pattern for data access

## RBAC

Roles are enforced via JWT dependencies:

- Admin: user management and all audit operations
- Auditor: controls, evidence, findings, dashboard
- Manager: inventory, findings, dashboard

## Configurable Controls

Controls can be added via `POST /api/v1/controls` with:

- `test_type`: automation key
- `weight`: risk scoring contribution
- `frameworks`: mappings to ISO 27001, NIST CSF, SOC 2, or other frameworks
- `parameters`: control-specific settings such as password age thresholds

## Tests

```bash
cd backend
pytest
```
