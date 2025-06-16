from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select

from core.db import get_async_session
from services.models import User

base_router = Router()

@base_router.message(Command("start"))
async def start(message: Message):
    user_id = message.from_user.id
    async with get_async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            user = User(telegram_id=user_id, name=message.from_user.username or "Anonymous")
            session.add(user)
            await session.commit()
    await message.reply(f"Привет, {user.name}! Используйте /help для списка команд.")
