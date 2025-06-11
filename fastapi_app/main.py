from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI

from bot.handlers import base_router
from services.handlers import router_quizzes
from core.config import settings
from core.init_db import create_first_superuser, init_db

bot = Bot(
    token=settings.telegram_bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_routers(
    base_router,
    router_quizzes,
    )

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    await init_db()
    await create_first_superuser()
    await bot.delete_webhook(drop_pending_updates=True)
    print("Starting polling...")
    polling_task = dp.start_polling(bot)
    yield
    await dp.stop_polling()
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.web_server_host,
        port=settings.web_server_port,
        log_level="info",
    )