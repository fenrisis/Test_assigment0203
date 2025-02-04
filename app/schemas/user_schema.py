# app/schemas/user_schema.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None

class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class User(UserInDB):
    """Схема для ответа API"""

