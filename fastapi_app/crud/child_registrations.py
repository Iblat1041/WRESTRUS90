from typing import Any, List, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from services.models import ChildRegistration


class CRUDChildRegistrations(CRUDBase):
    """Реализация CRUD для регистраций детей."""

    async def get_registration_by_id(
        self,
        reg_id: int,
        session: AsyncSession,
    ) -> ChildRegistration:
        """Получение регистрации по ID."""
        result = await session.execute(
            select(self.model).where(
                self.model.id == reg_id,),
        )
        return result.scalars().first()


    async def get_all_registrations(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 5,
    ) -> ChildRegistration:
        """Получение всех регистраций с пагинацией."""
        result = await session.execute(
            select(self.model)
            .offset(offset)
            .limit(limit)
            .order_by(self.model.created_at.desc()),
        )
        return result.scalars().all()


    async def get_registrations_count(
        self,
        session: AsyncSession,
    ) -> int:
        """Получение общего количества регистраций."""
        result = await session.execute(
            select(func.count()).select_from(self.model),
        )
        return result.scalar()


    async def update_registration_status(
        self,
        reg_id: int,
        status: str,
        session: AsyncSession,
    ) -> bool:
        """Обновление статуса регистрации."""
        registration = await self.get_registration_by_id(session, reg_id)
        if registration:
            registration.status = status
            await session.commit()
            await session.refresh(registration)
            return True
        return False


    async def create_registration(
        self,
        session: AsyncSession,
        **kwargs: dict[str, Any],
    ) -> ChildRegistration:
        """Создание новой регистрации."""
        registration = self.model(**kwargs)
        session.add(registration)
        await session.commit()
        await session.refresh(registration)
        return registration


    async def update_registration(
        self,
        reg_id: int,
        session: AsyncSession,
        **kwargs: dict[str, Any],
    ) -> Optional[ChildRegistration]:
        """Обновление объекта регистрации."""
        registration = await self.get_registration_by_id(session, reg_id)
        if registration:
            for key, value in kwargs.items():
                setattr(registration, key, value)
            await session.commit()
            await session.refresh(registration)
        return registration


child_reg_crud = CRUDChildRegistrations(ChildRegistration)