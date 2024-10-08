import uuid
from sqlalchemy import UUID, Column, String, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base


class Domain(Base):
    __tablename__ = "domain"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    scraped_at = Column(DateTime, server_default=func.now())
    