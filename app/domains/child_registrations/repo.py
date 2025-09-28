"""Репозиторий домена регистраций детей."""

from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.child_registrations.models import ChildRegistration


class ChildRegRepository:
    """Репозиторий регистраций детей."""

    model: type[ChildRegistration]

    def __init__(self, model: type[ChildRegistration]) -> None:
        self.model = model

    async def get_by_id(
        self,
        session: AsyncSession,
        reg_id: int,
    ) -> Optional[ChildRegistration]:
        """Получить регистрацию по ID."""
        result = await session.execute(
            select(self.model).where(self.model.id == reg_id)
        )
        return result.scalars().first()

    async def list(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[ChildRegistration]:
        """Список регистраций с пагинацией по дате создания (DESC)."""
        result = await session.execute(
            select(self.model)
            .order_by(self.model.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def count(self, session: AsyncSession) -> int:
        """Получить количество регистраций."""
        result = await session.execute(select(func.count()).select_from(self.model))
        return result.scalar() or 0

    async def create(
        self,
        session: AsyncSession,
        **kwargs: object,
    ) -> ChildRegistration:
        """Создать регистрацию."""
        obj = self.model(**kwargs)  # type: ignore[arg-type]
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def update_status(
        self,
        session: AsyncSession,
        reg_id: int,
        status: str,
    ) -> bool:
        """Обновить статус регистрации."""
        obj = await self.get_by_id(session, reg_id)
        if not obj:
            return False
        obj.status = status
        await session.commit()
        await session.refresh(obj)
        return True


child_reg_repo = ChildRegRepository(ChildRegistration)
