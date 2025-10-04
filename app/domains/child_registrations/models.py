"""Модели домена регистраций детей."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.domains.users.models import User


class ChildRegistration(Base):
    """Регистрация ребёнка в секцию."""

    __tablename__ = "child_registrations"

    # поля
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    child_name: Mapped[str] = mapped_column(String, nullable=False)
    child_surname: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_contact: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("pending", "approved", "rejected", name="registration_status"),
        default="pending",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # связь с пользователем
    user: Mapped["User"] = relationship(
        "User",
        back_populates="registrations",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<ChildRegistration id={self.id} child={self.child_name} {self.child_surname}>"
