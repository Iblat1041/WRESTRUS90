"""Модуль регистрации моделей для админ-панели fastadmin."""
from __future__ import annotations

from fastadmin import SqlAlchemyModelAdmin, register
from core.db import AsyncSessionLocal, Base, engine
from services.models import Admin, ChildRegistration, Event, News, User
import logging

# Используем логгер из конфигурации проекта
logger = logging.getLogger("my_app")

@register(Admin, sqlalchemy_sessionmaker=AsyncSessionLocal)
class AdminAdmin(SqlAlchemyModelAdmin):
    """Класс администрирования для модели Admin."""
    list_display = ["id", "user_id", "created_at"]
    username_field = "user.email"  # Ссылка на поле email через отношение
    password_field = "password"

    def __init__(self, *args, **kwargs):
        """Инициализация с логированием регистрации модели."""
        logger.info("Регистрация модели Admin")
        super().__init__(*args, **kwargs)

    def authenticate(self, username: str, password: str) -> bool:
        """
        Проверка учетных данных пользователя.

        Args:
            username (str): Имя пользователя (email).
            password (str): Пароль.

        Returns:
            bool: True, если аутентификация успешна, False иначе.
        """
        logger.info(f"Попытка аутентификации: username={username}, password=****")
        # Логика проверки (по умолчанию делегируется родительскому классу)
        result = super().authenticate(username, password)
        if not result:
            logger.warning(f"Аутентификация не удалась для username={username}")
        else:
            logger.info(f"Аутентификация успешна для username={username}")
        return result


@register(ChildRegistration, sqlalchemy_sessionmaker=AsyncSessionLocal)
class ChildRegistrationAdmin(SqlAlchemyModelAdmin):
    """Класс администрирования для модели ChildRegistration."""
    list_display = ["user_id", "child_name", "age", "parent_contact", "status", "created_at", "approved_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["child_name", "parent_contact", "status"]
    date_hierarchy = "created_at"

    def __init__(self, *args, **kwargs):
        """Инициализация с логированием регистрации модели."""
        logger.info("Регистрация модели ChildRegistration")
        super().__init__(*args, **kwargs)


@register(Event, sqlalchemy_sessionmaker=AsyncSessionLocal)
class EventAdmin(SqlAlchemyModelAdmin):
    """Класс администрирования для модели Event."""
    list_display = ["title", "date", "location", "created_at"]
    list_filter = ["date", "created_at"]
    search_fields = ["title", "location"]
    date_hierarchy = "date"

    def __init__(self, *args, **kwargs):
        """Инициализация с логированием регистрации модели."""
        logger.info("Регистрация модели Event")
        super().__init__(*args, **kwargs)


@register(News, sqlalchemy_sessionmaker=AsyncSessionLocal)
class NewsAdmin(SqlAlchemyModelAdmin):
    """Класс администрирования для модели News."""
    list_display = ["vk_post_id", "title", "status", "created_at", "published_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["title", "vk_post_id", "content"]
    date_hierarchy = "created_at"

    def __init__(self, *args, **kwargs):
        """Инициализация с логированием регистрации модели."""
        logger.info("Регистрация модели News")
        super().__init__(*args, **kwargs)


@register(User, sqlalchemy_sessionmaker=AsyncSessionLocal)
class UserAdmin(SqlAlchemyModelAdmin):
    """Класс администрирования для модели User."""
    list_display = ["telegram_id", "name", "email", "phone", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "email", "telegram_id"]
    date_hierarchy = "created_at"

    def __init__(self, *args, **kwargs):
        """Инициализация с логированием регистрации модели."""
        logger.info("Регистрация модели User")
        super().__init__(*args, **kwargs)