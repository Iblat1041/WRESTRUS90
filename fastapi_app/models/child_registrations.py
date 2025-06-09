from sqlalchemy import Column, DateTime, Enum, Integer, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.db import Base

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