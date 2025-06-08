from sqlalchemy import Column, DateTime, Integer, String, Text, JSON, Enum
from sqlalchemy.sql import func
from fastapi_app.core.config import Base

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    vk_post_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    images = Column(JSON, nullable=True)
    status = Column(Enum("pending", "approved", "rejected", name="news_status"), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)