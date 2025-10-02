# app/integrations/bot/main.py
import asyncio
import logging
from .api import setup_bot

logger = logging.getLogger("my_app.bot")
logger.setLevel(logging.INFO)


async def start_bot() -> None:
    """Запускает Telegram-бот.

    Raises:
        Exception: Если произошла ошибка при запуске бота.
    """
    logger.info("Starting Telegram bot")
    dp = await setup_bot()
    await dp.start_polling(dp.bot)


if __name__ == "__main__":
    asyncio.run(start_bot())
