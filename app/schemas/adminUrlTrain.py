import uuid
from pydantic import BaseModel
from datetime import datetime
    
    
class webUrlTrain(BaseModel):
    id: uuid.UUID
    url: str
    scraped_at: datetime