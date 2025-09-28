"""Модели домена событий (новости/соревнования/спонсоры)."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Enum, JSON, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class Event(Base):
    """Событие/публикация (VK)."""

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
