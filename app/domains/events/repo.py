"""Репозиторий домена событий."""

from __future__ import annotations

from typing import List, Optional

from aiocache import caches, cached
from aiocache.serializers import PickleSerializer
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.events.models import Event


class EventsRepository:
    """Репозиторий событий."""

    @cached(ttl=300, serializer=PickleSerializer(), namespace="events")
    async def list(
        self,
        session: AsyncSession,
        *,
        offset: int = 0,
        limit: int = 10,
        category: str | None = None,
        status: str | None = None,
    ) -> List[Event]:
        """Список событий с фильтрами."""
        query = select(Event).offset(offset).limit(limit).order_by(
            Event.published_at.desc().nullslast()
        )
        if category:
            query = query.where(Event.category == category)
        if status:
            query = query.where(Event.status == status)
        res = await session.execute(query)
        return list(res.scalars().all())

    @cached(ttl=300, serializer=PickleSerializer(), namespace="events")
    async def count(
        self,
        session: AsyncSession,
        *,
        category: str | None = None,
        status: str | None = None,
    ) -> int:
        """Подсчитать количество событий с фильтрами."""
        query = select(func.count()).select_from(Event)
        if category:
            query = query.where(Event.category == category)
        if status:
            query = query.where(Event.status == status)
        res = await session.execute(query)
        return res.scalar_one() or 0

    async def get(
        self,
        session: AsyncSession,
        event_id: int,
        *,
        status: str | None = None,
    ) -> Optional[Event]:
        """Получить событие по ID."""
        query = select(Event).where(Event.id == event_id)
        if status:
            query = query.where(Event.status == status)
        res = await session.execute(query)
        return res.scalars().first()

    async def set_status(
        self,
        session: AsyncSession,
        event_id: int,
        status: str,
    ) -> bool:
        """Обновить статус события и сбросить кэш."""
        result = await session.execute(
            update(Event).where(Event.id == event_id).values(status=status)
        )
        if result.rowcount == 0:
            return False
        await session.commit()
        await caches.get("default").clear(namespace="events")
        return True

    async def set_category(
        self,
        session: AsyncSession,
        event_id: int,
        category: str,
    ) -> bool:
        """Обновить категорию события и сбросить кэш."""
        result = await session.execute(
            update(Event).where(Event.id == event_id).values(category=category)
        )
        if result.rowcount == 0:
            return False
        await session.commit()
        await caches.get("default").clear(namespace="events")
        return True

    async def delete(self, session: AsyncSession, event_id: int) -> bool:
        """Удалить событие и сбросить кэш."""
        evt = await self.get(session, event_id)
        if not evt:
            return False
        await session.delete(evt)
        await session.commit()
        await caches.get("default").clear(namespace="events")
        return True


events_repo = EventsRepository()
