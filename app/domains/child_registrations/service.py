"""Бизнес-логика регистраций детей."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.child_registrations.models import ChildRegistration
from app.domains.child_registrations.repo import child_reg_repo
from app.domains.users.models import User


async def register_child(
    session: AsyncSession,
    user_tg_id: int,
    user_name: str,
    child_name: str,
    child_surname: str,
    age: int,
    parent_contact: str,
) -> ChildRegistration:
    """
    Создать регистрацию для ребёнка, автоматически создав пользователя при необходимости.
    """
    res = await session.execute(select(User).where(User.telegram_id == user_tg_id))
    user = res.scalar_one_or_none()
    if not user:
        user = User(telegram_id=user_tg_id, name=user_name, created_at=func.now())
        session.add(user)
        await session.flush()

    reg = await child_reg_repo.create(
        session=session,
        user_id=user.id,
        child_name=child_name,
        child_surname=child_surname,
        age=age,
        parent_contact=parent_contact,
        status="pending",
        created_at=func.now(),
    )
    return reg
