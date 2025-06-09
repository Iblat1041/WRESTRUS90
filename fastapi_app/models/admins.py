from sqlalchemy import Column, DateTime, Enum, Integer, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.db import Base

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    role = Column(Enum("admin", "moderator", name="admin_role"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связь с таблицей Users (опционально, для удобства)
    user = relationship("User", back_populates="admin_role")
