"""HTTP-эндпоинты домена регистраций детей."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db
from app.domains.child_registrations.repo import child_reg_repo
from app.domains.child_registrations.schemas import ChildRegRead

router = APIRouter(prefix="/child-registrations", tags=["child-registrations"])


@router.get("/", response_model=list[ChildRegRead])
async def list_child_regs(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
) -> list[ChildRegRead]:
    """Получить список регистраций детей."""
    regs = await child_reg_repo.list(session=session, offset=offset, limit=limit)
    return list(regs)
