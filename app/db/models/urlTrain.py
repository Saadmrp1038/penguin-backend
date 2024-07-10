import uuid
from sqlalchemy import UUID, Column, String, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base


class urltrain(Base):
    __tablename__ = "urltrain"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, nullable=False)
    scraped_at = Column(DateTime, server_default=func.now())
    