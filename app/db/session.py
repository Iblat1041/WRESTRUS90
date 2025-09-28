from __future__ import annotations

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import settings


engine = create_async_engine(
    settings.database_url,
    echo=True,          # выключай на проде
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@asynccontextmanager
async def get_async_session():
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Для совместимости
AsyncSessionLocal = async_session_maker
