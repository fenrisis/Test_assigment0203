# app/models/chat.py
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

chat_users = Table(
    "chat_users",
    Base.metadata,
    Column("chat_id", Integer, ForeignKey("chats.id", ondelete="CASCADE")),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
)


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    participants = relationship("User", secondary=chat_users, back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
