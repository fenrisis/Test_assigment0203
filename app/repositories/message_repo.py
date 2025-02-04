from datetime import UTC, datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_message(
        self,
        chat_id: int,
        sender_id: int,
        receiver_id: int,
        text: str,
    ) -> Message:
        message = Message(
            chat_id=chat_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            text=text,
            timestamp=datetime.now(UTC),
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_chat_messages(
        self,
        chat_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Message]:
        query = (
            select(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.timestamp.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
