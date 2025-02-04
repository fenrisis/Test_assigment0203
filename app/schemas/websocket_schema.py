# app/schemas/websocket_schema.py
from datetime import UTC, datetime

from pydantic import BaseModel


class WebSocketMessage(BaseModel):
    """Схема для WebSocket сообщений"""

    type: str  # message, typing, read
    chat_id: int
    content: str
    timestamp: datetime = datetime.now(UTC)


class WebSocketResponse(BaseModel):
    """Схема для ответов через WebSocket"""

    event: str
    data: dict
    timestamp: datetime = datetime.now(UTC)
