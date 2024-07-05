import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    name: str
    location: str
    email: str
    platform: Optional[str] = None
    interest: Optional[str] = None
    
class UserUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    platform: Optional[List[str]] = None
    interest: Optional[List[str]] = None
    
class User(BaseModel):
    id: uuid.UUID
    name: str
    location: str
    email: str
    platform: Optional[List[str]]
    interest: Optional[List[str]]
    
    created_at: datetime
    updated_at: datetime