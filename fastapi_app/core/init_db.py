from __future__ import annotations

from passlib.context import CryptContext
from sqlalchemy import select

from bot.logger import logger
from core.config import settings
from core.db import Base, engine, async_session_maker
from services.models import Admin, User

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    )

async def create_first_superuser() -> None:
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == settings.first_superuser_telegram_id),
        )
        if result.scalar_one_or_none():
            logger.info("Пользователь с таким Telegram ID уже существует")
            return

        # Создаём и сохраняем пользователя
        user = User(
            email=settings.first_superuser_email,
            name=f"{settings.first_superuser_first_name} {settings.first_superuser_last_name}",
            phone=settings.first_superuser_phone,
            telegram_id=settings.first_superuser_telegram_id,
        )
        session.add(user)
        await session.flush()  # Сохраняем user и получаем id
        logger.info(f"Создан пользователь: {user.name} ID: {user.id}")

        # Создаём и сохраняем администратора
        admin = Admin(
            user_id=user.id,

            password=pwd_context.hash(settings.first_superuser_password)
        )
        session.add(admin)
        await session.commit()  # Коммитим все изменения
        logger.info(f"Создан первый суперюзер: {user.name} Email: {user.email}")

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
