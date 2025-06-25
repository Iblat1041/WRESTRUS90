from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from services.models import ChildRegistration


async def get_all_registrations(session: AsyncSession, offset: int = 0, limit: int = 10) -> List[ChildRegistration]:
    """Получить список всех регистраций с пагинацией."""
    result = await session.execute(
        select(ChildRegistration).offset(offset).limit(limit).order_by(ChildRegistration.created_at.desc())
    )
    return result.scalars().all()


async def get_registrations_count(session: AsyncSession) -> int:
    """Получить общее количество регистраций."""
    result = await session.execute(select(func.count()).select_from(ChildRegistration))
    return result.scalar()


async def get_registration_by_id(session: AsyncSession, reg_id: int) -> Optional[ChildRegistration]:
    """Получить регистрацию по ID."""
    result = await session.execute(select(ChildRegistration).where(ChildRegistration.id == reg_id))
    return result.scalar_one_or_none()


async def update_registration_status(session: AsyncSession, reg_id: int, status: str) -> bool:
    """Обновить статус регистрации."""
    registration = await get_registration_by_id(session, reg_id)
    if registration:
        registration.status = status
        await session.commit()
        return True
    return False
