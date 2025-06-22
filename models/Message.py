from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    receiver_encrypted = Column(String)
    sender_encrypted = Column(String)
    message_type = Column(String, default="text")
    timestamp = Column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc))
    is_read = Column(Boolean, default=False)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    attachment = relationship("Attachment", back_populates="message", uselist=False)
