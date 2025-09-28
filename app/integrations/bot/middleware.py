"""Middleware для бота: БД-сессия и проверка роли."""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import async_session_maker
from app.domains.users.models import User

logger = logging.getLogger(__name__)


class DatabaseMiddleware(BaseMiddleware):
    """Добавляет объект AsyncSession в данные обработчика."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with async_session_maker() as session:
            data["session"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception:  # noqa: BLE001
                await session.rollback()
                logger.exception("Ошибка БД в middleware")
                raise


class RoleMiddleware(BaseMiddleware):
    """Определяет флаг is_admin и прикрепляет пользователя в data."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession | None = data.get("session")
        if not session or not getattr(event, "from_user", None):
            data["is_admin"] = False
            return await handler(event, data)

        result = await session.execute(
            select(User)
            .where(User.telegram_id == event.from_user.id)  # type: ignore[union-attr]
            .options(selectinload(User.admin_role))
        )
        user = result.scalars().first()
        data["user"] = user
        data["is_admin"] = bool(user and user.admin_role is not None)

        if (
            not data["is_admin"]
            and isinstance(event, CallbackQuery)
            and getattr(event, "data", "")  # noqa: B009
            and "admin" in event.data  # type: ignore[truthy-bool]
        ):
            await event.answer("У вас нет прав администратора.", show_alert=True)
            return

        return await handler(event, data)
