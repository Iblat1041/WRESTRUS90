import asyncio
import logging
import os
from celery import Celery
from celery.schedules import crontab
from core.config import settings
from core.logging_config import setup_logging
from vk.vk_service import VKService
from core.db import get_async_session
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Настройка логирования
setup_logging()
logger = logging.getLogger("my_app.celery")

# Инициализация Celery
celery_app = Celery(
    "vk_news",
    broker=settings.redis_url,  # Используем настройки из config
    backend=settings.redis_url,
    include=["vk.celery_app"],
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_track_started=True,
    task_create_missing_queues=True,
)

async def fetch_and_save_news_task_async():
    """Асинхронная задача для получения и сохранения новостей VK."""
    logger.info("Starting VK news fetch task")
    bot = None
    try:
        bot = Bot(
            token=settings.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        vk_service = VKService(bot=bot)

        # Получаем новости
        news = await vk_service.fetch_news(count=10)

        # Сохраняем новости в базу данных и отправляем уведомления
        async with get_async_session() as session:
            await vk_service.save_news_to_db(session, news)

        logger.info("VK news fetch task completed successfully")
        return {"status": "success", "count": len(news)}
    except Exception as e:
        logger.error(f"VK news fetch task failed: {str(e)}", exc_info=True)
        raise
    finally:
        if bot:
            await bot.session.close()

@celery_app.task(name="fetch_and_save_news_task", bind=True)
def fetch_and_save_news_task(self):
    """Синхронная обёртка для вызова асинхронной задачи с eventlet."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(fetch_and_save_news_task_async())
        return result
    except Exception as e:
        logger.error(f"Task failed: {str(e)}", exc_info=True)
        raise self.retry(exc=e, max_retries=3, countdown=5)
    finally:
        if 'loop' in locals() and not loop.is_closed():
            loop.close()

# Настройка Celery Beat
celery_app.conf.beat_schedule = {
    "fetch-vk-news-every-hour": {
        "task": "fetch_and_save_news_task",
        "schedule": crontab(minute=0, hour="*"),
        "options": {"expires": 60},
    },
}