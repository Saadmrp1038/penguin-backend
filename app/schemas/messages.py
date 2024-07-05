import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageCreate(BaseModel):
    chat_id: uuid.UUID
    sender: str = "user"
    content: str
    
class MessageUpdate(BaseModel):
    content: Optional[str] = None

class Message(BaseModel):
    id: uuid.UUID
    chat_id: uuid.UUID
    
    sender: str
    content: str
    knowledge: Optional[str]
    
    created_at: datetime
    updated_at: datetime