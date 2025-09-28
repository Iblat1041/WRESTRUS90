"""HTTP-эндпоинты домена пользователей."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db
from app.domains.users.repo import users_repo
from app.domains.users.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserRead])
async def list_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
) -> list[UserRead]:
    """Получить список пользователей."""
    users = await users_repo.list(session=session, offset=offset, limit=limit)
    return list(users)


@router.post("/", response_model=UserRead)
async def create_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_db),
) -> UserRead:
    """Создать нового пользователя."""
    user = await users_repo.create(session, **payload.model_dump())
    return user  # type: ignore[return-value]
