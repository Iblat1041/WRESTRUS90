from aiogram import BaseMiddleware

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core.db import async_session_maker  # Убедитесь, что путь к async_session_maker верен


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with async_session_maker() as session:
            data["session"] = session  # Передаем сессию в данные
            result = await handler(event, data)
            return result


class RoleMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        # Пример проверки роли (замените на свою логику)
        is_admin = False  # Здесь должна быть проверка из базы данных
        data["is_admin"] = is_admin
        if not is_admin and "admin" in data.get("callback_data", ""):
            await event.answer("У вас нет прав администратора.")
            return  # Прерываем обработку, если нет прав
        result = await handler(event, data)
        return result