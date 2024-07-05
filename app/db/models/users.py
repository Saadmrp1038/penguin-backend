import uuid
from sqlalchemy import Column, String, ARRAY, TIMESTAMP, UUID
from sqlalchemy.sql import func
from app.db.base_class import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    email = Column(String, nullable=False)
    platform = Column(ARRAY(String), nullable=True)
    interest = Column(ARRAY(String), nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())