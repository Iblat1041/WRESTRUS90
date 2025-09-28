"""Модели домена регистраций детей."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class ChildRegistration(Base):
    """Регистрация ребёнка в секцию."""

    __tablename__ = "child_registrations"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    child_name = Column(String, nullable=False)
    child_surname = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    parent_contact = Column(String, nullable=False)
    status = Column(
        Enum("pending", "approved", "rejected", name="registration_status"),
        default="pending",
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="registrations")
