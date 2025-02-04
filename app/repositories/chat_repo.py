# app/repositories/chat_repo.py
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import Chat
from app.models.user import User

from .base_repo import BaseRepository


class ChatRepository(BaseRepository[Chat]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Chat)

    async def create_chat(self, participant_ids: List[int]) -> Chat:
        # Получаем пользователей
        users_query = select(User).filter(User.id.in_(participant_ids))
        result = await self.session.execute(users_query)
        users = result.scalars().all()

        if len(users) != len(participant_ids):
            raise ValueError("Not all users found")

        # Создаём чат
        chat = Chat()
        chat.participants = users

        self.session.add(chat)
        await self.session.commit()
        await self.session.refresh(chat)
        return chat

    async def get_chat_with_participants(self, chat_id: int) -> Optional[Chat]:
        query = (
            select(self.model)
            .filter(self.model.id == chat_id)
            .options(selectinload(self.model.participants))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def add_participant(self, chat_id: int, user_id: int) -> bool:
        chat = await self.get_chat_with_participants(chat_id)
        if not chat:
            return False

        user_query = select(User).filter(User.id == user_id)
        result = await self.session.execute(user_query)
        user = result.scalar_one_or_none()

        if not user:
            return False

        chat.participants.append(user)
        await self.session.commit()
        return True

    async def remove_participant(self, chat_id: int, user_id: int) -> bool:
        chat = await self.get_chat_with_participants(chat_id)
        if not chat:
            return False

        chat.participants = [p for p in chat.participants if p.id != user_id]
        await self.session.commit()
        return True
