# app/schemas/chat_schema.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .user_schema import User


class ChatBase(BaseModel):
    pass


class ChatCreate(BaseModel):
    participant_ids: List[int]


class ChatUpdate(BaseModel):
    participant_ids: Optional[List[int]] = None


class ChatInDB(ChatBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Chat(ChatInDB):
    """Схема для ответа API"""

    participants: List[User]
