# app/integrations/bot/api.py
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from typing import List
import logging

from app.core.settings import settings
from .handlers.admin import admin_router
from .handlers.base import base_router, group_router
from .handlers.child import child_router
from .handlers.event import event_router
from .middleware import DatabaseMiddleware, RoleMiddleware

logger = logging.getLogger("my_app.bot.api")


async def setup_bot() -> Dispatcher:
    """Настраивает и возвращает диспетчер Telegram-бота.

    Returns:
        Dispatcher: Настроенный диспетчер aiogram.
    """
    logger.info("Setting up Telegram bot")
    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.message.middleware(RoleMiddleware())
    dp.callback_query.middleware(RoleMiddleware())
    dp.include_router(base_router)
    dp.include_router(group_router)
    dp.include_router(admin_router)
    dp.include_router(child_router)
    dp.include_router(event_router)

    private_commands: List[BotCommand] = [
        BotCommand(command="start", description="Начать взаимодействие с ботом"),
        BotCommand(command="menu", description="Открыть главное меню"),
    ]
    group_commands: List[BotCommand] = [
        BotCommand(command="menu", description="Открыть меню бота в группе"),
    ]
    await bot.set_my_commands(
        commands=private_commands, scope=types.BotCommandScopeAllPrivateChats()
    )
    await bot.set_my_commands(
        commands=group_commands, scope=types.BotCommandScopeAllGroupChats()
    )
    return dp
