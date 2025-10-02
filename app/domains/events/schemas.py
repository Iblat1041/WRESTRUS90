from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any
from enum import Enum


class NewsStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class NewsCategory(str, Enum):
    COMPETITION = "competition"
    EVENT = "event"
    SPONSOR = "sponsor"


class EventBase(BaseModel):
    """Базовая схема для события."""
    title: str
    content: str
    vk_post_id: Optional[str] = None
    images: Optional[List[Any]] = None  # JSON в БД, список в API
    status: NewsStatus = NewsStatus.ACTIVE
    category: NewsCategory = NewsCategory.COMPETITION


class EventCreate(EventBase):
    """Схема для создания события."""
    pass


class EventRead(EventBase):
    """Схема для чтения события."""
    id: int
    created_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Для сериализации SQLAlchemy-объектов
