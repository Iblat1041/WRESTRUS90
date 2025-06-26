from celery import Celery
from celery.schedules import crontab
from fastapi_app.core.config import settings
from fastapi_app.vk.vk_service import VKService
from fastapi_app.core.db import get_async_session
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode  # Добавлен импорт ParseMode
import logging

logger = logging.getLogger("my_app.celery")

celery_app = Celery(
    "vk_news",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["fastapi_app.celery_app"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task
async def fetch_and_save_news_task():
    """Задача для получения и сохранения новостей VK."""
    logger.info("Starting VK news fetch task")
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    vk_service = VKService(bot=bot)
    async with get_async_session() as session:
        try:
            news = await vk_service.fetch_news(count=10)
            await vk_service.save_news_to_db(session, news)
            logger.info("VK news fetch task completed successfully")
        except Exception as e:
            logger.error(f"VK news fetch task failed: {str(e)}")
            raise
        finally:
            await bot.session.close()

celery_app.conf.beat_schedule = {
    "fetch-vk-news-every-hour": {
        "task": "fastapi_app.celery_app.fetch_and_save_news_task",
        "schedule": crontab(minute=0, hour="*"),
    },
}
