from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChildRegBase(BaseModel):
    """Базовая схема для регистрации ребенка."""
    child_name: str
    child_surname: str
    age: int
    parent_contact: str
    user_id: int
    status: str = "pending"

class ChildRegCreate(ChildRegBase):
    """Схема для создания регистрации ребенка."""
    pass

class ChildRegRead(ChildRegBase):
    """Схема для чтения регистрации ребенка."""
    id: int
    created_at: datetime
    approved_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Для сериализации SQLAlchemy-объектов
