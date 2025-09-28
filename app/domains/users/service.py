"""Бизнес-логика домена пользователей."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.users.models import User
from app.domains.users.repo import users_repo


async def ensure_user(
    session: AsyncSession,
    telegram_id: int,
    name: str,
) -> User:
    """
    Гарантировать наличие пользователя по Telegram ID.

    Если не найден — создать.
    """
    user = await users_repo.get_by_telegram_id(session=session, telegram_id=telegram_id)
    if user:
        return user
    return await users_repo.create(session, telegram_id=telegram_id, name=name)


async def get_user_by_telegram(
    session: AsyncSession,
    telegram_id: int,
) -> Optional[User]:
    """Получить пользователя по Telegram ID (или None)."""
    return await users_repo.get_by_telegram_id(session=session, telegram_id=telegram_id)
