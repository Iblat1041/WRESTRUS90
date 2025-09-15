from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import logging
import logging.config

from core.logging_config import LOGGING_CONFIG, setup_logging

from bot.middleware import DatabaseMiddleware, RoleMiddleware
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from bot.handlers import base_router, group_router
from bot.keyboards import private_commands, group_commands
from core.config import settings
from core.init_db import create_first_superuser, init_db
from services import AdminAdmin, ChildRegistrationAdmin, EventAdmin, UserAdmin
from services import admin_router, child_router, event_router

# Настройка логирования
setup_logging()
logger = logging.getLogger("my_app")

# Инициализация бота
bot = Bot(
    token=settings.telegram_bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
storage = RedisStorage.from_url(settings.redis_url)
dp = Dispatcher(storage=storage)

# Регистрация маршрутов
dp.include_routers(
    admin_router,
    base_router,
    child_router,
    event_router,
    group_router,
)

# Применение middleware
dp.message.middleware(DatabaseMiddleware())
dp.message.middleware(RoleMiddleware())
dp.callback_query.middleware(DatabaseMiddleware())
dp.callback_query.middleware(RoleMiddleware())

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    """
    Контекстный менеджер для жизненного цикла приложения.

    Выполняет инициализацию базы данных, создание суперпользователя,
    настройку команд бота, запуск поллинга Telegram и очистку ресурсов при завершении.
    """
    logger.info("Инициализация базы данных...")
    await init_db()
    logger.info("Создание суперпользователя...")
    await create_first_superuser()
    logger.info("Удаление вебхука Telegram...")
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Настройка команд бота
    logger.info("Настройка команд бота...")
    try:
        # # Удаление старых команд для личных чатов
        # await bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
        # Установка новых команд для личных чатов
        await bot.set_my_commands(commands=private_commands, scope=BotCommandScopeAllPrivateChats())
        logger.debug("Successfully set commands for private chats")
        
        # # Удаление старых команд для групп
        # await bot.delete_my_commands(scope=BotCommandScopeAllGroupChats())
        # Установка новых команд для групп
        await bot.set_my_commands(commands=group_commands, scope=BotCommandScopeAllGroupChats())
        logger.debug("Successfully set commands for group chats")
    except Exception as e:
        logger.error(f"Failed to set bot commands: {str(e)}")
    
    logger.info("Запуск поллинга Telegram...")
    import asyncio
    polling_task = asyncio.create_task(dp.start_polling(bot))

    yield  # Передача управления приложению

    logger.info("Остановка приложения...")
    await dp.stop_polling()
    await polling_task
    await bot.session.close()

# Создание экземпляра приложения FastAPI
app = FastAPI(lifespan=lifespan)

# Настройка Prometheus метрик
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

if __name__ == "__main__":
    """Точка входа для запуска приложения с uvicorn."""
    logger.info(
        f"Запуск uvicorn на {settings.web_server_host}:{settings.web_server_port}"
    )
    uvicorn.run(
        app,
        host=settings.web_server_host,
        port=settings.web_server_port,
        log_config=LOGGING_CONFIG,
        log_level="info",
    )
