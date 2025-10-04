"""Модели домена пользователей."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:  # для подсказок типов, без жёсткого импорта
    from app.domains.child_registrations.models import ChildRegistration


class Admin(Base):
    """Модель роли администратора (привязка к User 1:1)."""

    __tablename__ = "admins"

    user_id: Mapped[int] = Column(
        Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True
    )
    password: Mapped[str] = Column(String, nullable=False)
    created_at: Mapped[str] = Column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Связь с пользователем (многие админы -> один пользователь), но фактически 1:1 через unique FK
    user: Mapped["User"] = relationship(
        "User",
        back_populates="admin_role",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Admin id={self.id} user_id={self.user_id}>"


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"

    telegram_id: Mapped[int | None] = Column(BigInteger, unique=True, index=True)
    name: Mapped[str] = Column(String, nullable=False)
    email: Mapped[str | None] = Column(String, unique=True, index=True)
    phone: Mapped[str | None] = Column(String, nullable=True)
    created_at: Mapped[str] = Column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Обратная связь с регистрациями детей
    registrations: Mapped[list["ChildRegistration"]] = relationship(
        "ChildRegistration",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # 1:1 роль админа
    admin_role: Mapped["Admin | None"] = relationship(
        "Admin",
        back_populates="user",
        uselist=False,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} tg={self.telegram_id} email={self.email!r}>"
