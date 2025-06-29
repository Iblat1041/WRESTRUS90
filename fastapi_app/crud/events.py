from typing import List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from services.models import Event
from .base import CRUDBase


class CRUDEvents(CRUDBase):
    """Класс для работы с моделью Event в базе данных."""

    async def get_all_events(self, session: AsyncSession, offset: int = 0, limit: int = 10) -> List[Event]:
        """Получить все мероприятия с пагинацией."""
        db_objs = await session.execute(
            select(self.model).offset(offset).limit(limit).order_by(self.model.created_at.desc())
        )
        return db_objs.scalars().all()

    async def get_events_count(self, session: AsyncSession) -> int:
        """Получить общее количество мероприятий."""
        result = await session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()

    async def get_event_by_id(self, session: AsyncSession, event_id: int) -> Event:
        """Получить мероприятие по ID."""
        db_obj = await session.execute(
            select(self.model).where(self.model.id == event_id)
        )
        return db_obj.scalars().first()

    async def update_event_status(self, session: AsyncSession, event_id: int, status: str) -> bool:
        """Обновить статус мероприятия."""
        db_obj = await self.get_event_by_id(session, event_id)
        if not db_obj:
            return False
        db_obj.status = status
        await session.commit()
        await session.refresh(db_obj)
        return True

    async def update_event_category(self, session: AsyncSession, event_id: int, category: str) -> bool:
        """Обновить категорию мероприятия."""
        db_obj = await self.get_event_by_id(session, event_id)
        if not db_obj:
            return False
        db_obj.category = category
        await session.commit()
        await session.refresh(db_obj)
        return True

    async def delete_event(self, session: AsyncSession, event_id: int) -> bool:
        """Удалить мероприятие."""
        db_obj = await self.get_event_by_id(session, event_id)
        if not db_obj:
            return False
        await session.delete(db_obj)
        await session.commit()
        return True


events_crud = CRUDEvents(Event)
