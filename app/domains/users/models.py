"""Модели домена пользователей."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:  # для подсказок типов, во избежание циклических импортов
    from app.domains.child_registrations.models import ChildRegistration


class Admin(Base):
    """Модель роли администратора."""

    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="admin_role")


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"

    telegram_id = Column(BigInteger, unique=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    registrations = relationship("ChildRegistration", back_populates="user")
    admin_role = relationship("Admin", back_populates="user", uselist=False)
