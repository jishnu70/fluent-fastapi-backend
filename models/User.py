from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    user_name = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)
    public_key = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))