# app/integrations/bot/middleware.py
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.db.session import async_session_maker
from .service import BotService

logger = logging.getLogger("my_app.bot.middleware")


class DatabaseMiddleware(BaseMiddleware):
    """Middleware для управления сессиями базы данных."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Добавляет сессию SQLAlchemy в контекст обработчика.

        Args:
            handler: Обработчик события.
            event: Событие от Telegram.
            data: Контекстные данные для обработчика.

        Returns:
            Any: Результат выполнения обработчика.
        """
        async with async_session_maker() as session:
            logger.debug("Session created in DatabaseMiddleware")
            data["session"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                logger.debug("Transaction committed successfully")
                return result
            except Exception as e:
                await session.rollback()
                logger.error(f"Database error: {e}", exc_info=True)
                raise
            finally:
                await session.close()
                logger.debug("Session closed")


class RoleMiddleware(BaseMiddleware):
    """Middleware для проверки ролей пользователей."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Проверяет роль пользователя и добавляет её в контекст.

        Args:
            handler: Обработчик события.
            event: Событие от Telegram.
            data: Контекстные данные для обработчика.

        Returns:
            Any: Результат выполнения обработчика или None, если доступ запрещён.
        """
        session: AsyncSession = data.get("session")
        if not session:
            logger.error("Session is missing in RoleMiddleware")
            raise ValueError("Сессия не предоставлена")
        if not hasattr(event, "from_user") or not event.from_user:
            logger.debug("No user associated with event, skipping RoleMiddleware")
            data["is_admin"] = False
            return await handler(event, data)
        bot_service = BotService()
        user = await bot_service.get_or_create_user(
            session, event.from_user.id, event.from_user.username
        )
        is_admin = user.admin_role is not None
        data["is_admin"] = is_admin
        data["user"] = user
        if not is_admin and isinstance(event, CallbackQuery) and "admin" in event.data:
            await event.answer("У вас нет прав администратора.", show_alert=True)
            return
        return await handler(event, data)
