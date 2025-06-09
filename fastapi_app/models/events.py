from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from core.db import Base

class Event(Base):
    __tablename__ = "events"

    title = Column(String, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    location = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
