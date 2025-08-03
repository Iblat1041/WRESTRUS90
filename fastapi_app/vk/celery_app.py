# /app/vk/celery_app.py
import asyncio
import logging
from celery import Celery
from celery.schedules import crontab
from core.config import settings
from vk.vk_service import VKService
from core.db import get_async_session
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

logger = logging.getLogger("my_app.celery")

# Инициализация Celery
celery_app = Celery(
    "vk_news",
    broker=settings.redis_url,
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
    task_concurrency=1,  # Ограничение на одну задачу за раз
    worker_pool="solo",  # Используем solo пул для избежания конкуренции
)

# Настройка движка базы данных
engine = create_async_engine(
    settings.database_url,
    echo=True,
    pool_size=5,  # Максимум 5 соединений
    max_overflow=10,  # Дополнительные соединения при необходимости
    pool_timeout=30,  # Таймаут ожидания соединения
)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def fetch_and_save_news_task_async():
    """Асинхронная задача для получения и сохранения новостей VK."""
    logger.info("Starting fetch_and_save_news_task_async")
    bot = None
    try:
        bot = Bot(
            token=settings.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        vk_service = VKService(bot=bot)
        news = await vk_service.fetch_news(count=10)
        async with async_session() as session:
            await vk_service.save_news_to_db(session, news)
        logger.info("Successfully completed fetch_and_save_news_task_async")
        return {"status": "success", "count": len(news)}
    except Exception as e:
        logger.error(f"Error in fetch_and_save_news_task_async: {str(e)}", exc_info=True)
        raise
    finally:
        if bot:
            await bot.session.close()

@celery_app.task(name="fetch_and_save_news_task", bind=True, max_retries=3)
def fetch_and_save_news_task(self):
    """Синхронная обёртка для вызова асинхронной задачи."""
    try:
        return asyncio.run(fetch_and_save_news_task_async())
    except Exception as e:
        logger.error(f"Task failed: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=5)
    finally:
        # Закрываем пул соединений
        asyncio.run(engine.dispose())

# Настройка Celery Beat
celery_app.conf.beat_schedule = {
    "fetch-vk-news-every-hour": {
        "task": "fetch_and_save_news_task",
        "schedule": crontab(minute=0, hour="*"),
        "options": {"expires": 300},
    },
}