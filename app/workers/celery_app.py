"""Инициализация Celery-приложения и расписания задач."""

from __future__ import annotations

import logging

from celery import Celery

from app.core.settings import settings

logger = logging.getLogger("my_app.celery")

celery_app = Celery(
    "vk_news",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["fastapi_app.workers.tasks.vk_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_track_started=True,
    task_create_missing_queues=True,
    task_concurrency=1,
    worker_pool="solo",
)

celery_app.conf.beat_schedule = {
    "fetch-vk-news-every-hour": {
        "task": "fetch_and_save_news_task",
        "schedule": 60 * 60,  # раз в час
        "options": {"expires": 300},
    },
}
