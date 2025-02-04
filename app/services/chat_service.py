# app/services/chat_service.py
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.chat_repo import ChatRepository
from app.repositories.user_repo import UserRepository
from app.schemas.chat_schema import Chat, ChatCreate


class ChatService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.chat_repo = ChatRepository(session)
        self.user_repo = UserRepository(session)

    async def create_chat(self, chat_data: ChatCreate) -> Chat:
        """Создание нового чата"""
        if len(chat_data.participant_ids) != 2:
            raise HTTPException(
                status_code=400,
                detail="Chat must have exactly 2 participants",
            )

        # Проверяем существование пользователей
        for user_id in chat_data.participant_ids:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail=f"User {user_id} not found",
                )

        return await self.chat_repo.create_chat(chat_data.participant_ids)

    async def get_chat(self, chat_id: int) -> Optional[Chat]:
        """Получение чата по ID"""
        chat = await self.chat_repo.get_chat_with_participants(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat

    async def get_user_chats(self, user_id: int) -> List[Chat]:
        """Получение всех чатов пользователя"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return await self.user_repo.get_user_chats(user_id)
