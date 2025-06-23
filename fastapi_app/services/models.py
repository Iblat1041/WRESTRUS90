from sqlalchemy import JSON, BigInteger, Column, DateTime, Enum, Integer, String, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.db import Base


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    password = Column(String, nullable=False)  # Хранит хешированный пароль
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="admin_role")


class ChildRegistration(Base):
    __tablename__ = "child_registrations"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    child_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    parent_contact = Column(String, nullable=False)
    status = Column(Enum("pending", "approved", "rejected", name="registration_status"), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)

    # Связь с таблицей Users (опционально, для удобства)
    user = relationship("User", back_populates="registrations")


class Event(Base):
    __tablename__ = "events"

    vk_post_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    images = Column(JSON, nullable=True)
    status = Column(Enum("active", "inactive", "pending", name="news_status"), default="active")
    category = Column(Enum("competition", "event", "sponsor", name="news_status"), default="competition")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)


class User(Base):
    __tablename__ = "users"

    telegram_id = Column(BigInteger, unique=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Обратные отношения
    registrations = relationship("ChildRegistration", back_populates="user")
    admin_role = relationship("Admin", back_populates="user", uselist=False)
