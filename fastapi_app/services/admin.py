from __future__ import annotations
from fastadmin import SqlAlchemyModelAdmin, register
from core.db import AsyncSessionLocal
from services.models import Admin, ChildRegistration, Event, User
import logging

logger = logging.getLogger("my_app")

# Проверка импортов моделей
logger.info(f"Imported models: Admin={Admin}, ChildRegistration={ChildRegistration}, Event={Event}, User={User}")


@register(Admin, sqlalchemy_sessionmaker=AsyncSessionLocal)
class AdminAdmin(SqlAlchemyModelAdmin):
    list_display = ["id", "user_id", "created_at"]
    username_field = "user.email"
    password_field = "password"

    def __init__(self, *args, **kwargs):
        logger.info(f"Registering AdminAdmin with model: {Admin}")
        super().__init__(*args, **kwargs)

    def authenticate(self, username: str, password: str) -> bool:
        logger.info(f"Attempting authentication: username={username}")
        result = super().authenticate(username, password)
        logger.info(f"Authentication {'successful' if result else 'failed'} for username={username}")
        return result


@register(ChildRegistration, sqlalchemy_sessionmaker=AsyncSessionLocal)
class ChildRegistrationAdmin(SqlAlchemyModelAdmin):
    list_display = ["user_id", "child_name", "age", "parent_contact", "status", "created_at", "approved_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["child_name", "parent_contact", "status"]
    date_hierarchy = "created_at"

    def __init__(self, *args, **kwargs):
        logger.info(f"Registering ChildRegistrationAdmin with model: {ChildRegistration}")
        super().__init__(*args, **kwargs)


@register(Event, sqlalchemy_sessionmaker=AsyncSessionLocal)
class EventAdmin(SqlAlchemyModelAdmin):
    list_display = ["title", "date", "location", "created_at"]
    list_filter = ["date", "created_at"]
    search_fields = ["title", "location"]
    date_hierarchy = "date"

    def __init__(self, *args, **kwargs):
        logger.info(f"Registering EventAdmin with model: {Event}")
        super().__init__(*args, **kwargs)


@register(User, sqlalchemy_sessionmaker=AsyncSessionLocal)
class UserAdmin(SqlAlchemyModelAdmin):
    list_display = ["telegram_id", "name", "email", "phone", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "email", "telegram_id"]
    date_hierarchy = "created_at"

    def __init__(self, *args, **kwargs):
        logger.info(f"Registering UserAdmin with model: {User}")
        super().__init__(*args, **kwargs)