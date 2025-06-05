from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageCreate(BaseModel):
    receiverID: int
    content: str
    messageType: str
    attachmentID: Optional[int] = None

class MessageResponse(BaseModel):
    senderID: int
    receiverID: int
    content: str
    messageType: str
    attachmentID: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True  # Needed to return SQLAlchemy model instances
        allow_population_by_field_name = True