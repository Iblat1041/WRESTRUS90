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
from fastadmin import fastapi_app as admin_app
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from bot.handlers import base_router
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
storage = RedisStorage.from_url(settings.redis_url)  # Используем redis_url из settings
dp = Dispatcher(storage=storage)

# Регистрация маршрутов
dp.include_routers(
    admin_router,
    base_router,
    child_router,
    event_router
    )

# Применение middleware
dp.message.middleware(DatabaseMiddleware())  # Сначала DatabaseMiddleware
dp.message.middleware(RoleMiddleware())      # Затем RoleMiddleware
dp.callback_query.middleware(DatabaseMiddleware())  # Сначала DatabaseMiddleware
dp.callback_query.middleware(RoleMiddleware())      # Затем RoleMiddleware


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
        log_config=LOGGING_CONFIG,  # Передача конфигурации логирования
        log_level="info",  # Синхронизация с конфигурацией
    )
