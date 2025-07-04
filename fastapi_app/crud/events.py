from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer
from enum import Enum
from typing import List, Optional
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from services.models import Event
from .base import CRUDBase
import logging

logger = logging.getLogger(__name__)

class EventCategory(Enum):
    COMPETITION = "competition"
    EVENT = "event"
    SPONSOR = "sponsor"


class CRUDEvents(CRUDBase):
    @cached(ttl=300, serializer=PickleSerializer(), namespace="events")
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


    @cached(ttl=300, serializer=PickleSerializer(), namespace="events")
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
            category=EventCategory.COMPETITION.value,
            status="active"
        )


    async def get_event_by_id(
        self,
        session: AsyncSession,
        event_id: int,
        status: str | None = None
    ) -> Optional[Event]:
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
            logger.warning(f"Event with id={event_id} not found for status update")
            return False
        await session.commit()
        logger.info(f"Successfully updated status for event_id={event_id} to {status}")
        await Cache(Cache.MEMORY).delete(f"get_all_events:{status}:active")
        await Cache(Cache.MEMORY).delete(f"get_events_count:{status}:active")
        return True


    async def update_event_category(self, session: AsyncSession, event_id: int, category: str, commit: bool = True) -> bool:
        """Обновить категорию мероприятия."""
        try:
            if category not in [c.value for c in EventCategory]:
                logger.error(f"Invalid category provided: {category}")
                raise ValueError(f"Недопустимая категория: {category}. Допустимые значения: {[c.value for c in EventCategory]}")
            
            logger.debug(f"Updating category for event_id={event_id} to category={category}")
            result = await session.execute(
                update(self.model).where(self.model.id == event_id).values(category=category)
            )
            if result.rowcount == 0:
                logger.warning(f"Event with id={event_id} not found for category update")
                return False
            
            if commit:
                await session.commit()
                logger.info(f"Successfully updated category for event_id={event_id} to {category}")
                await Cache(Cache.MEMORY).delete(f"get_all_events:{category}:active")
                await Cache(Cache.MEMORY).delete(f"get_events_count:{category}:active")
            return True
        
        except Exception as e:
            logger.error(f"Error updating category for event_id={event_id}: {e}", exc_info=True)
            raise


    async def delete_event(self, session: AsyncSession, event_id: int) -> bool:
        """Удалить мероприятие."""
        db_obj = await self.get_event_by_id(session, event_id)
        if not db_obj:
            logger.warning(f"Event with id={event_id} not found for deletion")
            return False
        await session.delete(db_obj)
        await session.commit()
        logger.info(f"Successfully deleted event_id={event_id}")
        await Cache(Cache.MEMORY).delete(f"get_all_events:{db_obj.category}:active")
        await Cache(Cache.MEMORY).delete(f"get_events_count:{db_obj.category}:active")
        return True

events_crud = CRUDEvents(Event)