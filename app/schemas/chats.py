import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Any, Dict, Optional, List

class Message(BaseModel):
    content: Dict[str, Any]

class ChatCreate(BaseModel):
    user_id: uuid.UUID
    name: str
    messages: List[Message]
    
class ChatUpdate(BaseModel):
    messages: List[Message]

class Chat(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    messages: List[Message]
    
    created_at: datetime
    updated_at: datetime