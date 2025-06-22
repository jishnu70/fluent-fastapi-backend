from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from schemas.PartnerSchema import PartnerInfoResponse

class MessageCreate(BaseModel):
    receiverID: int
    receiver_encrypted: str
    sender_encrypted: str
    messageType: str
    # attachmentID: Optional[int] = None

class MessageResponse(BaseModel):
    senderID: int = Field(...,alias="sender_id")
    receiverID: int = Field(...,alias="receiver_id")
    content: str
    messageType: str = Field(...,alias="message_type")
    # attachmentID: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True  # Needed to return SQLAlchemy model instances
        validate_by_name = True

class MessageChatList(BaseModel):
    partner: PartnerInfoResponse
    message: MessageResponse
