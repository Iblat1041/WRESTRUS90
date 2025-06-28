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
    broker="redis://localhost:6379/0",  # Для локального запуска
    backend="redis://localhost:6379/0",
    include=["fastapi_app.vk.celery_app"],
)

# celery_app = Celery(
#     "vk_news",
#     broker="redis://redis:6379/0",
#     backend="redis://redis:6379/0",
#     include=["fastapi_app.celery_app"],
# )

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)

# Декорируем задачу с явным именем
@celery_app.task(name="fetch_and_save_news_task")
def fetch_and_save_news_task():
    """Задача для получения и сохранения новостей VK."""
    logger.info("Starting VK news fetch task")
    try:
        # Создаём событийный цикл
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Инициализируем сервисы
        bot = Bot(
            token=settings.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        vk_service = VKService(bot=bot)

        # Выполняем асинхронные операции
        news = loop.run_until_complete(vk_service.fetch_news(count=10))
        session = loop.run_until_complete(get_async_session().__aenter__())
        try:
            loop.run_until_complete(vk_service.save_news_to_db(session, news))
        finally:
            loop.run_until_complete(session.__aexit__(None, None, None))

        # Отправляем уведомление в Telegram
        loop.run_until_complete(bot.__aenter__())
        try:
            for event in news:
                loop.run_until_complete(
                    bot.send_message(
                        chat_id=settings.first_superuser_telegram_id,
                        text=f"Новое событие: {event.get('text', 'Без заголовка')[:100]}\nID: {event['id']}",
                    )
                )
        finally:
            loop.run_until_complete(bot.__aexit__(None, None, None))

        logger.info("VK news fetch task completed successfully")
        return {"status": "success", "count": len(news)}
    except Exception as e:
        logger.error(f"VK news fetch task failed: {str(e)}", exc_info=True)
        raise
    finally:
        if not loop.is_closed():
            loop.close()

# Единственный beat_schedule
celery_app.conf.beat_schedule = {
    "fetch-vk-news-every-hour": {
        "task": "fetch_and_save_news_task",
        "schedule": crontab(minute=0, hour="*"),
        "options": {
            "expires": 60,  # Задача истекает через 60 секунд
        }
    },
}