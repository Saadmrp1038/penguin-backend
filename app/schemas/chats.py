import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Any, Dict, Optional, List

class ChatCreate(BaseModel):
    user_id: uuid.UUID
    name: str
    messages: List[Dict[str, Any]]
    
class ChatUpdate(BaseModel):
    messages: List[Dict[str, Any]]

class Chat(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    messages: List[Dict[str, Any]]
    
    created_at: datetime
    updated_at: datetime
    
class ChatPreview(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    
    created_at: datetime
    updated_at: datetime