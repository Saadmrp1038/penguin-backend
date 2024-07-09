import uuid
from sqlalchemy import UUID, Column, ForeignKey, String, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base


class Issue(Base):
    __tablename__ = "issues"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id"), nullable=False)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=False)
    
    message_content = Column(String, nullable=False) #for heading purposes
    
    feedback = Column(String, nullable=True)
    response = Column(String, nullable=True)
    
    status = Column(String, nullable=False) #open, resolved
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    