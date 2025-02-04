from datetime import datetime
from typing import List

from pydantic import BaseModel


class MessageBase(BaseModel):
    text: str


class MessageCreate(MessageBase):
    chat_id: int
    receiver_id: int


class Message(MessageBase):
    id: int
    chat_id: int
    sender_id: int
    receiver_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class MessageList(BaseModel):
    messages: List[Message]
