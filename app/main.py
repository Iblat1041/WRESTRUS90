# app/main.py
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
import asyncio
import logging

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand, BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.router import api_router
from app.core.logging_config import LOGGING_CONFIG, setup_logging
from app.core.settings import settings
from app.db.init_db import create_first_superuser, init_db
from app.integrations.bot.handlers.admin import admin_router
from app.integrations.bot.handlers.base import base_router, group_router
from app.integrations.bot.handlers.child import child_router
from app.integrations.bot.handlers.event import event_router
from app.integrations.bot.middleware import DatabaseMiddleware, RoleMiddleware

setup_logging()
logger = logging.getLogger("my_app")


# Инициализация бота и диспетчера
bot = Bot(
    token=settings.telegram_bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
storage = RedisStorage.from_url(settings.redis_url)
dp = Dispatcher(storage=storage)

# Регистрация роутеров бота
dp.include_routers(
    admin_router,
    base_router,
    child_router,
    event_router,
    group_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    """Управляет жизненным циклом приложения.

    Инициализирует базу данных, создаёт суперпользователя, настраивает команды
    Telegram-бота и запускает поллинг.

    Args:
        app: FastAPI-приложение.

    Yields:
        None: Выполняет действия до завершения приложения.
    """
    logger.info("Инициализация базы данных...")
    await init_db()
    logger.info("Создание суперпользователя...")
    await create_first_superuser()

    logger.info("Удаление вебхука Telegram...")
    await bot.delete_webhook(drop_pending_updates=True)

    # Настройка команд бота
    private_commands = [
        BotCommand(command="start", description="Начать взаимодействие с ботом"),
        BotCommand(command="menu", description="Открыть главное меню"),
    ]
    group_commands = [
        BotCommand(command="menu", description="Открыть меню бота в группе"),
    ]
    try:
        await bot.set_my_commands(
            commands=private_commands,
            scope=BotCommandScopeAllPrivateChats(),
        )
        await bot.set_my_commands(
            commands=group_commands,
            scope=BotCommandScopeAllGroupChats(),
        )
    except Exception as e:
        logger.exception(f"Не удалось установить команды бота: {e}")

    # Middleware бота
    dp.message.middleware(DatabaseMiddleware())
    dp.message.middleware(RoleMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(RoleMiddleware())

    logger.info("Запуск поллинга Telegram...")
    polling_task = asyncio.create_task(dp.start_polling(bot))

    yield

    logger.info("Остановка приложения...")
    await dp.stop_polling()
    await polling_task
    await bot.session.close()


app = FastAPI(title="WRESTRUS90 API", lifespan=lifespan)
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
