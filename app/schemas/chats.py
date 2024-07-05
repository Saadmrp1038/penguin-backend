import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.schemas.messages import Message

class ChatCreate(BaseModel):
    user_id: uuid.UUID
    name: str
    
class ChatUpdate(BaseModel):
    name: Optional[str] = None

class Chat(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    
    name: str
    
    created_at: datetime
    updated_at: datetime
    
class ChatWithMessages(Chat):
    messages: List[Message]