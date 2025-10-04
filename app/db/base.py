"""Общий базовый класс ORM и загрузка всех моделей."""

from __future__ import annotations

from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base, declared_attr


class PreBase:
    """Миксин: задаёт имя таблицы и первичный ключ."""

    @declared_attr
    def __tablename__(cls) -> str:  # noqa: N805
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


# Все ваши модели должны наследоваться от Base
Base = declarative_base(cls=PreBase)


def load_all_models() -> None:
    """
    Импортировать все модули с ORM-моделями,
    чтобы они были зарегистрированы в реестре мапперов SQLAlchemy.
    """
    # ВАЖНО: импортируйте здесь все домены с моделями.
    import app.domains.users.models  # noqa: F401
    import app.domains.child_registrations.models  # noqa: F401
