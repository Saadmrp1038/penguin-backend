import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
    
class QuestionCreate(BaseModel):
    question: str
    answer: Optional[str] = None
    url: Optional[str] = None
    
class QuestionUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    url: Optional[str] = None
    
class Question(BaseModel):
    id: uuid.UUID
    question: str
    answer: Optional[str]
    url: Optional[str]
    
    created_at: datetime
    updated_at: datetime