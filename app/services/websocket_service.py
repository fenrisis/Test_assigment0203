from datetime import UTC, datetime
from typing import Dict, Optional, Set

from fastapi import WebSocket

from app.schemas.websocket_schema import WebSocketMessage, WebSocketResponse


class WebSocketManager:
    def __init__(self):
        self._active_connections: Dict[int, WebSocket] = {}
        self._user_chats: Dict[int, Set[int]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self._active_connections[user_id] = websocket
        self._user_chats[user_id] = set()

    def disconnect(self, user_id: int):
        if user_id in self._active_connections:
            del self._active_connections[user_id]
        if user_id in self._user_chats:
            del self._user_chats[user_id]

    def add_user_to_chat(self, user_id: int, chat_id: int):
        if user_id in self._user_chats:
            self._user_chats[user_id].add(chat_id)

    async def broadcast_to_chat(
            self,
            message: WebSocketMessage,
            exclude_user_id: Optional[int] = None,
    ):
        # Создаем ответ с текущим временем
        response = WebSocketResponse(
            event="message",
            data=message.model_dump() | {"timestamp": datetime.now(UTC)},
            timestamp=datetime.now(UTC),
        )

        json_response = response.model_dump_json()

        for user_id, chats in self._user_chats.items():
            if (
                    user_id != exclude_user_id and
                    message.chat_id in chats and
                    user_id in self._active_connections
            ):
                await self._active_connections[user_id].send_text(json_response)

    async def send_personal_message(
            self,
            user_id: int,
            message: str,
    ):
        if user_id in self._active_connections:
            await self._active_connections[user_id].send_text(message)
