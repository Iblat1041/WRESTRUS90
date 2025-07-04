from __future__ import annotations

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from core.logging_config import setup_logging, LOGGING_CONFIG
from core.config import settings
from core.db import Base, engine, async_session_maker
from services.models import Admin, User
import logging

# Настройка логирования
setup_logging()
logger = logging.getLogger("my_app.init_db")

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)

async def create_first_superuser() -> None:
    """Создаёт первого суперпользователя, если он ещё не существует."""
    logger.info("Starting creation of first superuser")
    async with async_session_maker() as session:
        try:
            result = await session.execute(
                select(User).where(
                    User.telegram_id == settings.first_superuser_telegram_id
                )
            )
            if result.scalar_one_or_none():
                logger.info(
                    f"User with Telegram ID {settings.first_superuser_telegram_id} already exists"
                )
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
            logger.info(f"Created user: {user.name} ID: {user.id}")

            # Создаём и сохраняем администратора
            admin = Admin(
                user_id=user.id,
                password=pwd_context.hash(settings.first_superuser_password),
            )
            session.add(admin)
            await session.commit()  # Коммитим все изменения
            logger.info(f"Created first superuser: {user.name} Email: {user.email}")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create superuser: {str(e)}", exc_info=True)
            await session.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error during superuser creation: {str(e)}", exc_info=True)
            await session.rollback()
            raise

async def init_db() -> None:
    """Инициализирует базу данных, создавая все таблицы."""
    logger.info("Initializing database...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except SQLAlchemyError as e:
        logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {str(e)}", exc_info=True)
        raise
