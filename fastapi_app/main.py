#!/usr/bin/env python3
"""Основной файл приложения FastAPI с интеграцией aiogram и fastadmin."""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import logging
import logging.config

from core.logging_config import LOGGING_CONFIG

from bot.middleware import DatabaseMiddleware, RoleMiddleware
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from fastadmin import fastapi_app as admin_app
from fastapi import FastAPI

from bot.handlers import base_router
from core.config import settings
from core.init_db import create_first_superuser, init_db
from services import AdminAdmin, ChildRegistrationAdmin, EventAdmin, UserAdmin
from services import admin_router

# Настройка централизованного логирования
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("my_app")  # Используем логгер 'my_app' из конфигурации


# Инициализация бота
bot = Bot(
    token=settings.telegram_bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация маршрутов
dp.include_routers(
    admin_router,
    base_router,
    )

# Применение middleware
dp.message.middleware(RoleMiddleware())
dp.message.middleware(DatabaseMiddleware())
dp.callback_query.middleware(RoleMiddleware())
dp.callback_query.middleware(DatabaseMiddleware())


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    """
    Контекстный менеджер для жизненного цикла приложения.

    Выполняет инициализацию базы данных, создание суперпользователя,
    запуск поллинга Telegram и очистку ресурсов при завершении.
    """
    logger.info("Инициализация базы данных...")
    await init_db()
    logger.info("Создание суперпользователя...")
    await create_first_superuser()
    logger.info("Удаление вебхука Telegram...")
    await bot.delete_webhook(drop_pending_updates=True)
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
logger.info("Монтирование админ-панели fastadmin...")
app.mount("/admin", admin_app)


if __name__ == "__main__":
    """Точка входа для запуска приложения с uvicorn."""
    logger.info(
        f"Запуск uvicorn на {settings.web_server_host}:{settings.web_server_port}"
    )
    uvicorn.run(
        app,
        host=settings.web_server_host,
        port=settings.web_server_port,
        log_config=LOGGING_CONFIG,  # Передача конфигурации логирования
        log_level="info",  # Синхронизация с конфигурацией
    )