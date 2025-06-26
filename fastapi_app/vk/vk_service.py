import aiohttp
import time
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from fastapi_app.services.models import Event
from fastapi_app.core.config import settings
from sqlalchemy import select
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from aiogram import Bot
from prometheus_client import Counter, Histogram
import logging

logger = logging.getLogger("my_app.vk_service")

# Prometheus метрики
vk_requests_total = Counter(
    "vk_api_requests_total",
    "Total VK API requests",
    ["status"]
    )
vk_request_duration = Histogram(
    "vk_api_request_duration_seconds",
    "VK API request duration"
    )

class VKService:
    def __init__(self, bot: Bot = None):
        self.base_url = "https://api.vk.com/method"
        self.access_token = settings.vk_access_token
        self.group_id = settings.vk_group_id
        self.bot = bot

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=10),
        retry=retry_if_exception_type(aiohttp.ClientError),
        before_sleep=lambda retry_state: logger.warning(
            f"Retrying VK API request (attempt {retry_state.attempt_number})..."
        ),
    )
    async def fetch_news(self, count: int = 10) -> list[dict]:
        """Получение новостей из группы VK с повторными попытками."""
        logger.info(f"Fetching {count} news from VK group {self.group_id}")
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "access_token": self.access_token,
                    "v": "5.131",
                    "owner_id": f"-{self.group_id}",
                    "count": count,
                    "extended": 1,
                }
                async with session.get(f"{self.base_url}/wall.get", params=params) as response:
                    vk_request_duration.observe(time.time() - start_time)
                    if response.status == 200:
                        data = await response.json()
                        if "error" in data:
                            error_msg = data["error"]["error_msg"]
                            logger.error(f"VK API error: {error_msg}")
                            vk_requests_total.labels(status="error").inc()
                            raise Exception(f"VK API error: {error_msg}")
                        vk_requests_total.labels(status="success").inc()
                        return data.get("response", {}).get("items", [])
                    else:
                        logger.error(f"VK API request failed with status {response.status}")
                        vk_requests_total.labels(status="error").inc()
                        raise Exception(f"VK API error: {response.status}")
        except Exception:
            vk_request_duration.observe(time.time() - start_time)
            raise

    async def save_news_to_db(self, session: AsyncSession, news: list[dict]):
        """Сохранение новостей в таблицу Events и отправка уведомлений."""
        logger.info(f"Saving {len(news)} news items to database")
        new_events = []
        for item in news:
            existing_event = await session.execute(
                select(Event).filter_by(vk_post_id=str(item["id"]))
            )
            if existing_event.scalar_one_or_none():
                logger.debug(f"Skipping existing post with vk_post_id {item['id']}")
                continue

            images = []
            if "attachments" in item:
                for attachment in item.get("attachments", []):
                    if attachment["type"] == "photo":
                        sizes = attachment["photo"]["sizes"]
                        largest = max(sizes, key=lambda x: x["width"] * x["height"])
                        images.append(largest["url"])

            event = Event(
                vk_post_id=str(item["id"]),
                title=item.get("text", "")[:100] or "Без заголовка",
                content=item.get("text", "") or "Без текста",
                images=images,
                status="active",
                category="event",
                created_at=datetime.utcnow(),
                published_at=datetime.fromtimestamp(item["date"]) if item["date"] else None,
            )
            session.add(event)
            new_events.append(event)
            logger.debug(f"Added new event with vk_post_id {item['id']}")

        await session.commit()
        logger.info("News saved successfully")

        # Отправка уведомлений администраторам
        if self.bot and new_events:
            for event in new_events:
                try:
                    await self.bot.send_message(
                        chat_id=settings.first_superuser_telegram_id,
                        text=f"Новое событие: {event.title}\nID: {event.vk_post_id}",
                    )
                    logger.info(f"Sent Telegram notification for event {event.vk_post_id}")
                except Exception as e:
                    logger.error(f"Failed to send Telegram notification: {str(e)}")
