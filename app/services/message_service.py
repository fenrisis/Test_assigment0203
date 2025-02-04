# app/services/message_service.py

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.chat_repo import ChatRepository
from app.repositories.message_repo import MessageRepository
from app.schemas.message_schema import Message, MessageCreate, MessageList


class MessageService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.message_repo = MessageRepository(session)
        self.chat_repo = ChatRepository(session)

    async def create_message(
        self,
        message_data: MessageCreate,
        sender_id: int,
    ) -> Message:
        """Создание нового сообщения"""
        # Проверяем существование чата
        chat = await self.chat_repo.get_chat_with_participants(message_data.chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        # Проверяем, что отправитель является участником чата
        if sender_id not in [p.id for p in chat.participants]:
            raise HTTPException(
                status_code=403,
                detail="Sender is not a participant of this chat",
            )

        # Проверяем, что получатель является участником чата
        if message_data.receiver_id not in [p.id for p in chat.participants]:
            raise HTTPException(
                status_code=403,
                detail="Receiver is not a participant of this chat",
            )

        return await self.message_repo.create_message(
            chat_id=message_data.chat_id,
            sender_id=sender_id,
            receiver_id=message_data.receiver_id,
            text=message_data.text,
        )

    async def get_chat_history(
        self,
        chat_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> MessageList:
        """Получение истории сообщений чата"""
        # Проверяем существование чата
        chat = await self.chat_repo.get_by_id(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        messages = await self.message_repo.get_chat_messages(
            chat_id=chat_id,
            limit=limit,
            offset=offset,
        )

        return MessageList(messages=messages)
