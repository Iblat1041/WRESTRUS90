"""Слой доступа к данным (репозиторий) домена пользователей."""

from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.users.models import User


class UsersRepository:
    """Репозиторий пользователей."""

    model: type[User]

    def __init__(self, model: type[User]) -> None:
        """Инициализировать репозиторий с моделью."""
        self.model = model

    async def get_by_telegram_id(
        self,
        session: AsyncSession,
        telegram_id: int,
    ) -> Optional[User]:
        """Найти пользователя по Telegram ID."""
        result = await session.execute(
            select(self.model).where(self.model.telegram_id == telegram_id)
        )
        return result.scalars().first()

    async def get_by_id(self, session: AsyncSession, user_id: int) -> Optional[User]:
        """Найти пользователя по ID."""
        result = await session.execute(
            select(self.model).where(self.model.id == user_id)
        )
        return result.scalars().first()

    async def list(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[User]:
        """Получить список пользователей с пагинацией."""
        result = await session.execute(
            select(self.model).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def count(self, session: AsyncSession) -> int:
        """Получить количество пользователей."""
        result = await session.execute(select(func.count()).select_from(self.model))
        return result.scalar() or 0

    async def create(self, session: AsyncSession, **kwargs: object) -> User:
        """Создать пользователя."""
        user = self.model(**kwargs)  # type: ignore[arg-type]
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def update(
        self,
        session: AsyncSession,
        user_id: int,
        **kwargs: object,
    ) -> Optional[User]:
        """Обновить пользователя по ID."""
        user = await session.get(self.model, user_id)
        if not user:
            return None
        for key, value in kwargs.items():
            setattr(user, key, value)
        await session.commit()
        await session.refresh(user)
        return user


users_repo = UsersRepository(User)
