"""Модели домена событий (новости/соревнования/спонсоры)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class Event(Base):
    """Событие/публикация (например, из VK)."""

    __tablename__ = "events"

    vk_post_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    images: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    status: Mapped[str] = mapped_column(
        Enum("active", "inactive", "pending", name="news_status"),
        default="active",
    )
    category: Mapped[str] = mapped_column(
        Enum("competition", "event", "sponsor", name="news_category"),
        default="competition",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"<Event id={self.id} vk_post_id={self.vk_post_id} status={self.status}>"
