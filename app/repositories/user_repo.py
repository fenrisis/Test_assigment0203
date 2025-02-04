from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User

from .base_repo import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_username(self, username: str) -> Optional[User]:
        query = select(self.model).filter(self.model.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_chats(self, user_id: int) -> List[User]:
        query = (
            select(self.model)
            .filter(self.model.id == user_id)
            .options(selectinload(self.model.chats))
        )
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        return user.chats if user else []
