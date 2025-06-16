from __future__ import annotations

from fastadmin import SqlAlchemyModelAdmin, register
from core.db import AsyncSessionLocal, Base, engine
from services.models import Admin, ChildRegistration, Event, News, User
# Функция для получения сессии (опционально, если требуется кастомная логика)

# Регистрация модели Admin
@register(Admin, sqlalchemy_sessionmaker=AsyncSessionLocal)
class AdminAdmin(SqlAlchemyModelAdmin):
    list_display = ["id", "user_id", "created_at"]
    username_field = "user.email"  # Ссылка на поле email через отношение
    password_field = "password"


# Регистрация модели ChildRegistration
@register(ChildRegistration, sqlalchemy_sessionmaker=AsyncSessionLocal)
class ChildRegistrationAdmin(SqlAlchemyModelAdmin):
    list_display = ["user_id", "child_name", "age", "parent_contact", "status", "created_at", "approved_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["child_name", "parent_contact", "status"]
    # Фильтр для дат
    date_hierarchy = "created_at"


# Регистрация модели Event
@register(Event, sqlalchemy_sessionmaker=AsyncSessionLocal)
class EventAdmin(SqlAlchemyModelAdmin):
    list_display = ["title", "date", "location", "created_at"]
    list_filter = ["date", "created_at"]
    search_fields = ["title", "location"]
    date_hierarchy = "date"


# Регистрация модели News
@register(News, sqlalchemy_sessionmaker=AsyncSessionLocal)
class NewsAdmin(SqlAlchemyModelAdmin):
    list_display = ["vk_post_id", "title", "status", "created_at", "published_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["title", "vk_post_id", "content"]
    date_hierarchy = "created_at"


# Регистрация модели User
@register(User, sqlalchemy_sessionmaker=AsyncSessionLocal)
class UserAdmin(SqlAlchemyModelAdmin):
    list_display = ["telegram_id", "name", "email", "phone", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "email", "telegram_id"]
    date_hierarchy = "created_at"

