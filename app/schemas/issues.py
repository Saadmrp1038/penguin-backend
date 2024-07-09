import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.schemas.chats import ChatWithMessages

class IssueCreate(BaseModel):
    user_id : uuid.UUID
    chat_id : uuid.UUID
    message_id : uuid.UUID
    
    message_content : str
    
    feedback : Optional[str] = None

class IssueUpdate(BaseModel):
    response : Optional[str] = None
    status : Optional[str] = None
  
class Issue(BaseModel):
    id : uuid.UUID
    user_id : uuid.UUID
    chat_id : uuid.UUID
    message_id : uuid.UUID
    
    message_content : str
    
    feedback : Optional[str] = None
    response : Optional[str] = None
    
    status : str
    
    created_at: datetime
    updated_at: datetime
    
class IssueWithChat(Issue):
    chat: ChatWithMessages