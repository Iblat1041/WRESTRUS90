from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, declared_attr
from contextlib import asynccontextmanager

from core.config import settings

class PreBase:
    """Базовый класс для всех моделей с автоматическим именем таблицы и полем ID."""
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)

# Создаём базовый класс для моделей
Base = declarative_base(cls=PreBase)

# Настройка асинхронного движка
engine = create_async_engine(
    settings.database_url,
    echo=True,  # Для отладки, можно отключить в продакшене
    pool_size=5,  # Ограничение пула соединений
    max_overflow=10,
)

# Фабрика асинхронных сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@asynccontextmanager
async def get_async_session():
    """Контекстный менеджер для работы с асинхронной сессией."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

# Для обратной совместимости
AsyncSessionLocal = async_session_maker