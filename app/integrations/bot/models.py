# app/integrations/bot/models.py
from pydantic import BaseModel, Field
from typing import Optional


class BotUser(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    name: str = Field(default="Anonymous", min_length=1)


class ChildRegistrationInput(BaseModel):
    child_name: str = Field(..., min_length=1)
    child_surname: str = Field(..., min_length=1)
    age: int = Field(..., gt=0, lt=150)
    parent_contact: str = Field(..., min_length=1)


class EventFilter(BaseModel):
    category: str
    status: str = "active"
    offset: int = 0
    limit: int = 5
