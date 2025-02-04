# app/api/message_api.py
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.message_schema import MessageList
from app.services.message_service import MessageService

router = APIRouter(prefix="/api", tags=["messages"])


@router.get(
    "/history/{chat_id}",
    response_model=MessageList,
    description="Get chat message history with pagination",
)
async def get_chat_history(
        chat_id: int,
        limit: Optional[int] = Query(default=50, ge=1, le=100),
        offset: Optional[int] = Query(default=0, ge=0),
        db: AsyncSession = Depends(get_db),
):
    """Get chat message history with pagination.

    Args:
        chat_id: ID of the chat
        limit: Maximum number of messages to return (default: 50)
        offset: Number of messages to skip (default: 0)

    Returns:
        List of messages sorted by timestamp in ascending order

    """
    message_service = MessageService(db)

    # message history
    return await message_service.get_chat_history(
        chat_id=chat_id,
        limit=limit,
        offset=offset,
    )
