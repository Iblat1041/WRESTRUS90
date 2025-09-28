"""Pydantic-схемы домена пользователей."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Базовые поля пользователя (общие для чтения/создания)."""

    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """Схема создания пользователя."""

    telegram_id: int


class UserRead(UserBase):
    """Схема чтения пользователя."""

    id: int
    telegram_id: int

    class Config:
        from_attributes = True
