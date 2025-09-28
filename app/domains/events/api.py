"""HTTP-эндпоинты домена событий."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db
from app.domains.events.repo import events_repo
from app.domains.events.schemas import EventRead

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=list[EventRead])
async def list_events(
    category: str | None = None,
    status: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> list[EventRead]:
    """Получить список событий с фильтрами и пагинацией."""
    events = await events_repo.list(
        session=session,
        offset=offset,
        limit=limit,
        category=category,
        status=status,
    )
    return events  # type: ignore[return-value]
