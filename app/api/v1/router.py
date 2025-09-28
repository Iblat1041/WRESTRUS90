"""Маршрутизатор v1: сборка роутов доменов."""

from __future__ import annotations

from fastapi import APIRouter

from app.domains.child_registrations.api import router as child_regs_router
from app.domains.events.api import router as events_router
from app.domains.users.api import router as users_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(users_router)
api_router.include_router(events_router)
api_router.include_router(child_regs_router)
