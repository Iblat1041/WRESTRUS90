
from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, declared_attr
from contextlib import asynccontextmanager


class PreBase:
    """Базовый класс для всех моделей с автоматическим именем таблицы и полем ID."""
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)

# Создаём базовый класс для моделей
Base = declarative_base(cls=PreBase)