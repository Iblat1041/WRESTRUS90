"""Инициализация БД и создание первого суперпользователя."""

from __future__ import annotations

import logging

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.core.logging_config import setup_logging
from app.core.settings import settings
from app.db.base import Base, load_all_models
from app.db.session import async_session_maker, engine
from app.domains.users.models import Admin, User

setup_logging()
logger = logging.getLogger("my_app.init_db")

# Настройка хеширования паролей админов
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


async def create_first_superuser() -> None:
    """
    Создать первого суперпользователя, если он отсутствует.

    Логика:
    1) Проверяем, есть ли пользователь с заданным Telegram ID.
    2) Если нет — создаём User и связанную запись Admin с паролем.
    """
    logger.info("Создание суперпользователя...")
    # Гарантируем, что все модели подгружены (важно для relationship со строковыми ссылками)
    load_all_models()

    async with async_session_maker() as session:
        try:
            result = await session.execute(
                select(User).where(
                    User.telegram_id == settings.first_superuser_telegram_id
                )
            )
            if result.scalar_one_or_none() is not None:
                logger.info("Суперпользователь уже существует")
                return

            user = User(
                email=settings.first_superuser_email,
                name=f"{settings.first_superuser_first_name} "
                f"{settings.first_superuser_last_name}",
                phone=settings.first_superuser_phone,
                telegram_id=settings.first_superuser_telegram_id,
            )
            session.add(user)
            await session.flush()  # нужно для получения user.id

            admin = Admin(
                user_id=user.id,
                password=pwd_context.hash(settings.first_superuser_password),
            )
            session.add(admin)

            await session.commit()
            logger.info("Суперпользователь создан")
        except SQLAlchemyError:  # noqa: PERF203
            await session.rollback()
            logger.exception("Ошибка создания суперпользователя")
            raise


async def init_db() -> None:
    """
    Создать таблицы БД (если не используете Alembic на старте).

    Важно: заранее подгружаем все модели, чтобы Base.metadata знала о них.
    """
    logger.info("Инициализация базы данных...")
    try:
        load_all_models()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Инициализация БД завершена")
    except Exception:  # noqa: BLE001
        logger.exception("Ошибка инициализации БД")
        raise
