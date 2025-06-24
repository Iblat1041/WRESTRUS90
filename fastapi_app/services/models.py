from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy import JSON, String, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from core.db import Base

if TYPE_CHECKING:
    from .models import Admin, ChildRegistration, User


class Admin(Base):
    """Модель для администраторов системы."""

    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    password = Column(String, nullable=False)  # Хранит хешированный пароль
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="admin_role")


class ChildRegistration(Base):
    """Модель для регистрации детей в секции."""

    __tablename__ = "child_registrations"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    child_name = Column(String, nullable=False)
    child_surname = Column(String, nullable=False)  # Новое поле для фамилии
    age = Column(Integer, nullable=False)
    parent_contact = Column(String, nullable=False)
    status = Column(
        Enum("pending", "approved", "rejected", name="registration_status"),
        default="pending",
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="registrations")


class Event(Base):
    """Модель для событий (соревнования, новости, спонсоры)."""

    __tablename__ = "events"

    vk_post_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    images = Column(JSON, nullable=True)
    status = Column(
        Enum("active", "inactive", "pending", name="news_status"),
        default="active",
    )
    category = Column(
        Enum("competition", "event", "sponsor", name="news_category"),
        default="competition",
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)


class User(Base):
    """Модель для пользователей системы."""

    __tablename__ = "users"

    telegram_id = Column(BigInteger, unique=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    registrations = relationship("ChildRegistration", back_populates="user")
    admin_role = relationship("Admin", back_populates="user", uselist=False)