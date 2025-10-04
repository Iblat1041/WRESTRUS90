# app/integrations/bot/service.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Tuple, Optional
import logging

from app.domains.child_registrations.models import ChildRegistration
from app.domains.child_registrations.repo import ChildRegRepository
from app.domains.events.models import Event
from app.domains.events.repo import events_repo
from app.domains.users.models import User
from app.domains.users.service import ensure_user

from .models import BotUser, ChildRegistrationInput, EventFilter

logger = logging.getLogger("my_app.bot.service")


class BotService:
    """Сервисный слой для бизнес-логики Telegram-бота."""

    async def get_or_create_user(
        self, session: AsyncSession, telegram_id: int, username: Optional[str]
    ) -> User:
        """Получает или создает пользователя по Telegram ID.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            telegram_id: ID пользователя в Telegram.
            username: Имя пользователя Telegram (может быть None).

        Returns:
            User: Объект пользователя из базы данных.
        """
        user_data = BotUser(telegram_id=telegram_id, username=username)
        return await ensure_user(
            session, telegram_id=user_data.telegram_id, name=user_data.name
        )

    async def register_child(
        self, session: AsyncSession, user_id: int, data: ChildRegistrationInput
    ) -> ChildRegistration:
        """Регистрирует ребенка для пользователя.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            user_id: ID пользователя в базе данных.
            data: Данные для регистрации ребенка.

        Returns:
            ChildRegistration: Зарегистрированная запись ребенка.
        """
        child_reg = ChildRegistration(
            user_id=user_id,
            child_name=data.child_name,
            child_surname=data.child_surname,
            age=data.age,
            parent_contact=data.parent_contact,
            status="pending",
        )
        session.add(child_reg)
        await session.commit()
        return child_reg

    async def list_events(
        self, session: AsyncSession, filter: EventFilter
    ) -> Tuple[List[Event], int]:
        """Получает список событий с учетом фильтров.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            filter: Фильтры для выборки событий (категория, статус, пагинация).

        Returns:
            Tuple[List[Event], int]: Список событий и общее количество записей.
        """
        events = await events_repo.list(
            session,
            offset=filter.offset,
            limit=filter.limit,
            category=filter.category,
            status=filter.status,
        )
        total = await events_repo.count(
            session, category=filter.category, status=filter.status
        )
        return events, total

    async def list_child_registrations(
        self, session: AsyncSession, offset: int, limit: int
    ) -> Tuple[List[ChildRegistration], int]:
        """Получает список регистраций детей с пагинацией.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            offset: Смещение для пагинации.
            limit: Лимит записей на страницу.

        Returns:
            Tuple[List[ChildRegistration], int]: Список регистраций и общее количество.
        """
        registrations = await child_registrations_repo.list(
            session, offset=offset, limit=limit
        )
        total = await child_registrations_repo.count(session)
        return registrations, total

    async def list_users(
        self, session: AsyncSession, offset: int, limit: int
    ) -> Tuple[List[User], int]:
        """Получает список пользователей с пагинацией.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            offset: Смещение для пагинации.
            limit: Лимит записей на страницу.

        Returns:
            Tuple[List[User], int]: Список пользователей и общее количество.
        """
        from app.domains.users.repo import users_repo

        users = await users_repo.list(session, offset=offset, limit=limit)
        total = await users_repo.count(session)
        return users, total

    async def update_child_registration_status(
        self, session: AsyncSession, reg_id: int, status: str
    ) -> bool:
        """Обновляет статус регистрации ребенка.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            reg_id: ID записи регистрации.
            status: Новый статус ('approved', 'rejected', 'pending').

        Returns:
            bool: True, если обновление успешно, иначе False.
        """
        registration = await child_registrations_repo.get_by_id(session, reg_id)
        if not registration:
            return False
        registration.status = status
        await session.commit()
        return True

    async def update_event_status_or_category(
        self, session: AsyncSession, event_id: int, field: str, value: str
    ) -> bool:
        """Обновляет статус или категорию события.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            event_id: ID события.
            field: Поле для обновления ('status' или 'category').
            value: Новое значение поля.

        Returns:
            bool: True, если обновление успешно, иначе False.
        """
        event = await events_repo.get_by_id(session, event_id)
        if not event:
            return False
        if field == "status" and value in ["active", "inactive", "pending"]:
            event.status = value
        elif field == "category" and value in ["competition", "event", "sponsor"]:
            event.category = value
        else:
            return False
        await session.commit()
        return True

    async def delete_event(self, session: AsyncSession, event_id: int) -> bool:
        """Удаляет событие по ID.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            event_id: ID события.

        Returns:
            bool: True, если удаление успешно, иначе False.
        """
        event = await events_repo.get_by_id(session, event_id)
        if not event:
            return False
        await session.delete(event)
        await session.commit()
        return True