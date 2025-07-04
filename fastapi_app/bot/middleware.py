import logging
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

from sqlalchemy import select
from core.db import async_session_maker
from sqlalchemy.orm import selectinload
from services.models import User

logger = logging.getLogger(__name__)

class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with async_session_maker() as session:
            logger.debug("Session created in DatabaseMiddleware: %s", type(session))
            data["session"] = session
            try:
                # Вызываем следующий обработчик
                result = await handler(event, data)
                await session.commit()
                logger.debug("Transaction committed successfully")
                return result
            except Exception as e:
                await session.rollback()
                logger.error("Database error: %s", str(e), exc_info=True)
                raise
            finally:
                await session.close()
                logger.debug("Session closed")


class RoleMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        session = data.get("session")
        if not session:
            logger.error("Session is missing in RoleMiddleware")
            raise ValueError("Сессия не предоставлена")

        # Проверка наличия from_user
        if not hasattr(event, "from_user") or not event.from_user:
            logger.debug("No user associated with event, skipping RoleMiddleware")
            data["is_admin"] = False
            return await handler(event, data)

        user_id = event.from_user.id
        result = await session.execute(
            select(User).where(User.telegram_id == user_id).options(selectinload(User.admin_role))
        )
        user = result.scalars().first()
        is_admin = user and user.admin_role is not None
        data["is_admin"] = is_admin
        data["user"] = user  # Сохраняем user для использования в обработчиках

        if not is_admin and isinstance(event, CallbackQuery) and "admin" in event.data:
            await event.answer("У вас нет прав администратора.", show_alert=True)
            return

        return await handler(event, data)
