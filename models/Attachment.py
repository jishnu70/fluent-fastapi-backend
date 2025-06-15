from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    file_name = Column(String)
    file_type = Column(String)  # "image/png", "application/pdf", etc.
    file_url = Column(String)  # Or `ipfs_hash` if using IPFS
    encryption_key = Column(String, nullable=True)  # if using hybrid encryption

    message = relationship("Message", backref="attachment")
