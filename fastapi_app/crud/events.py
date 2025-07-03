from typing import List
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from services.models import Event
from .base import CRUDBase


class CRUDEvents(CRUDBase):
    """Класс для работы с моделью Event в базе данных."""

    async def get_all_events(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 10,
        category: str | None = None,
        status: str | None = None
    ) -> List[Event]:
        """Получить все мероприятия с пагинацией и опциональной фильтрацией."""
        query = select(self.model).offset(offset).limit(limit).order_by(self.model.published_at.desc())
        if category:
            query = query.where(self.model.category == category)
        if status:
            query = query.where(self.model.status == status)
        db_objs = await session.execute(query)
        return db_objs.scalars().all()


    async def get_events_count(
        self,
        session: AsyncSession,
        category: str | None = None,
        status: str | None = None
    ) -> int:
        """Получить общее количество мероприятий с опциональной фильтрацией."""
        query = select(func.count()).select_from(self.model)
        if category:
            query = query.where(self.model.category == category)
        if status:
            query = query.where(self.model.status == status)
        result = await session.execute(query)
        return result.scalar_one()


    async def get_total_active_competitions(self, session: AsyncSession) -> int:
        """Возвращает общее количество активных соревнований."""
        return await self.get_events_count(
            session=session,
            category="competition", 
            status="active"
        )


    async def get_event_by_id(
        self,
        session: AsyncSession,
        event_id: int,
        status: str | None = None
    ) -> Event | None:
        """Получить мероприятие по ID с опциональной фильтрацией по статусу."""
        query = select(self.model).where(self.model.id == event_id)
        if status:
            query = query.where(self.model.status == status)
        db_obj = await session.execute(query)
        return db_obj.scalars().first()


    async def update_event_status(self, session: AsyncSession, event_id: int, status: str) -> bool:
        """Обновить статус мероприятия."""
        result = await session.execute(
            update(self.model).where(self.model.id == event_id).values(status=status)
        )
        if result.rowcount == 0:
            return False
        await session.commit()
        return True


    async def update_event_category(self, session: AsyncSession, event_id: int, category: str) -> bool:
        """Обновить категорию мероприятия."""
        result = await session.execute(
            update(self.model).where(self.model.id == event_id).values(category=category)
        )
        if result.rowcount == 0:
            return False
        await session.commit()
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