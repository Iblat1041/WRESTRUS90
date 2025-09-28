"""Точка входа: FastAPI-приложение + запуск Telegram-бота в lifespan."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.router import api_router
from app.core.logging_config import LOGGING_CONFIG, setup_logging
from app.core.settings import settings
from app.db.init_db import create_first_superuser, init_db
from app.integrations.bot.admin import admin_router
from app.integrations.bot.commands import group_commands, private_commands
from app.integrations.bot.handlers import base_router, group_router
from app.integrations.bot.middleware import DatabaseMiddleware, RoleMiddleware
from app.integrations.bot.child import child_router

setup_logging()
logger = logging.getLogger("my_app")

bot = Bot(
    token=settings.telegram_bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
storage = RedisStorage.from_url(settings.redis_url)
dp = Dispatcher(storage=storage)

# Регистрация роутеров бота
dp.include_routers(admin_router, base_router, child_router, group_router)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    """
    Жизненный цикл приложения:
    - инициализация БД,
    - создание суперпользователя,
    - настройка команд бота,
    - запуск поллинга.
    """
    logger.info("Инициализация БД...")
    await init_db()
    logger.info("Создание суперпользователя...")
    await create_first_superuser()

    logger.info("Удаление вебхука Telegram...")
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await bot.set_my_commands(private_commands, scope=BotCommandScopeAllPrivateChats())
        await bot.set_my_commands(group_commands, scope=BotCommandScopeAllGroupChats())
    except Exception:  # noqa: BLE001
        logger.exception("Не удалось установить команды бота")

    # Middleware бота
    dp.message.middleware(DatabaseMiddleware())
    dp.message.middleware(RoleMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(RoleMiddleware())

    logger.info("Запуск поллинга Telegram...")
    import asyncio
    polling_task = asyncio.create_task(dp.start_polling(bot))

    yield

    logger.info("Остановка приложения...")
    await dp.stop_polling()
    await polling_task
    await bot.session.close()


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

# Метрики Prometheus
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

if __name__ == "__main__":
    logger.info("Запуск uvicorn...")
    uvicorn.run(
        app,
        host=settings.web_server_host,
        port=settings.web_server_port,
        log_config=LOGGING_CONFIG,
        log_level="info",
    )
