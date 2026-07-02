from fastapi import APIRouter

from app.api.routes import auth, controls, dashboard, evidence, findings, inventory, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(inventory.router)
api_router.include_router(controls.router)
api_router.include_router(evidence.router)
api_router.include_router(findings.router)
api_router.include_router(dashboard.router)
