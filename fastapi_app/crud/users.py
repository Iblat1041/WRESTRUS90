from typing import Any, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from services.models import User


class CRUDUsers(CRUDBase):
    """Реализация CRUD для юзеров."""

    async def get_user_by_telegram_id(
        self,
        telegram_id: int,
        session: AsyncSession,
    ) -> Optional[User]:
        """Получение юзера по telegram id."""
        result = await session.execute(
            select(self.model).where(
                self.model.telegram_id == telegram_id,
            ),
        )
        return result.scalars().first()

    async def get_user_by_id(
        self,
        user_id: int,
        session: AsyncSession,
    ) -> Optional[User]:
        """Получение юзера по id."""
        result = await session.execute(
            select(self.model).where(
                self.model.id == user_id,
            ),
        )
        return result.scalars().first()

    async def get_all_users(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 5,
    ) -> Sequence[User]:
        """Получение юзеров с ограничением выборки."""
        result = await session.execute(
            select(self.model).offset(offset).limit(limit),
        )
        return result.scalars().all()

    async def get_users_count(
        self,
        session: AsyncSession,
    ) -> int:
        """Получение количества юзеров."""
        result = await session.execute(
            select(
                func.count(),
            ).select_from(self.model),
        )
        return result.scalar()

    async def create_user(
        self,
        session: AsyncSession,
        **kwargs: dict[str, Any],
    ) -> User:
        """Создание юзера, тестовая версия."""
        user = self.model(**kwargs)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def update_user(
            self,
            user_id: int,
            session: AsyncSession,
            **kwargs: dict[str, Any],
    ) -> Optional[User]:
        """Обновление объекта юзера."""
        user = await session.get(self.model, user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            await session.commit()
            await session.refresh(user)
        return user


users_crud = CRUDUsers(User)
