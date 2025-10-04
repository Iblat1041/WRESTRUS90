# app/integrations/bot/models.py
from pydantic import BaseModel, Field
from typing import Optional


class BotUser(BaseModel):
    """Модель для валидации данных пользователя Telegram."""
    telegram_id: int = Field(..., description="ID пользователя в Telegram")
    username: Optional[str] = Field(None, description="Имя пользователя Telegram")
    name: str = Field(default="Anonymous", min_length=1, description="Имя пользователя")


class ChildRegistrationInput(BaseModel):
    """Модель для валидации данных регистрации ребенка."""
    child_name: str = Field(..., min_length=1, description="Имя ребенка")
    child_surname: str = Field(..., min_length=1, description="Фамилия ребенка")
    age: int = Field(..., gt=0, lt=150, description="Возраст ребенка")
    parent_contact: str = Field(..., min_length=1, description="Контакт родителя")


class EventFilter(BaseModel):
    """Модель для фильтрации событий."""
    category: str = Field(..., description="Категория события")
    status: str = Field("active", description="Статус события")
    offset: int = Field(0, ge=0, description="Смещение для пагинации")
    limit: int = Field(5, gt=0, description="Лимит записей на страницу")