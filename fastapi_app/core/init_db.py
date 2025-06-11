from __future__ import annotations

from passlib.context import CryptContext
from sqlalchemy import select

from bot.logger import logger
from core.config import settings
from core.db import Base, get_async_session, engine
from services.models import Admin, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

async def create_first_superuser() -> None:
    async with get_async_session() as session:
        result = await session.execute(
            select(User).where(User.email == settings.first_superuser_email)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            logger.info("Суперпользователь с таким email уже существует")
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
            role=settings.first_superuser_role,
            password=pwd_context.hash(settings.first_superuser_password)
        )
        session.add(admin)
        await session.commit()  # Коммитим все изменения
        logger.info(f"Создан первый суперюзер: {user.name} Email: {user.email}")

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
