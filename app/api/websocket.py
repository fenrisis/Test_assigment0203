# app/api/websocket.py
import json

from fastapi import Depends, HTTPException, WebSocket, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketDisconnect

from app.database import get_db
from app.schemas.message_schema import MessageCreate
from app.schemas.websocket_schema import WebSocketMessage
from app.services.chat_service import ChatService
from app.services.message_service import MessageService
from app.services.websocket_service import WebSocketManager
from app.utils.logger import logger

websocket_manager = WebSocketManager()


async def handle_websocket_message(
        data: dict,
        user_id: int,
        message_service: MessageService,
        chat_service: ChatService,
) -> WebSocketMessage:
    """Обработка входящего WebSocket сообщения"""
    try:
        message_data = WebSocketMessage(**data)
        logger.info(f"Processing message from user {user_id}: {data}")

        # Проверяем доступ к чату
        chat = await chat_service.get_chat(message_data.chat_id)
        if user_id not in [p.id for p in chat.participants]:
            logger.warning(f"User {user_id} attempted to access chat {message_data.chat_id} without permission")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a participant of this chat",
            )

        # Создаем сообщение в БД
        if message_data.type == "message":
            # Находим receiver_id (второй участник чата)
            receiver_id = next(
                p.id for p in chat.participants
                if p.id != user_id
            )
            logger.info(f"Creating message: sender={user_id}, receiver={receiver_id}, chat={message_data.chat_id}")

            await message_service.create_message(
                MessageCreate(
                    chat_id=message_data.chat_id,
                    text=message_data.content,
                    receiver_id=receiver_id,
                ),
                sender_id=user_id,
            )

        return message_data

    except ValueError as e:
        logger.error(f"Invalid message format from user {user_id}: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


async def websocket_endpoint(
        websocket: WebSocket,
        user_id: int,
        db: AsyncSession = Depends(get_db),
):
    """WebSocket endpoint для обмена сообщениями"""
    try:
        logger.info(f"New WebSocket connection request from user {user_id}")

        # Инициализируем сервисы
        message_service = MessageService(db)
        chat_service = ChatService(db)

        # Проверяем существование пользователя через чат-сервис
        user_chats = await chat_service.get_user_chats(user_id)
        logger.info(f"User {user_id} has {len(user_chats)} chats")

        # Подключаем пользователя
        await websocket_manager.connect(websocket, user_id)
        logger.info(f"User {user_id} connected successfully")

        # Добавляем пользователя во все его чаты
        for chat in user_chats:
            websocket_manager.add_user_to_chat(user_id, chat.id)
            logger.info(f"User {user_id} added to chat {chat.id}")

        try:
            while True:
                # Получаем сообщение
                data = await websocket.receive_text()
                logger.debug(f"Received raw message from user {user_id}: {data}")
                message_data = json.loads(data)

                # Обрабатываем сообщение
                processed_message = await handle_websocket_message(
                    message_data,
                    user_id,
                    message_service,
                    chat_service,
                )

                # Отправляем сообщение в чат
                await websocket_manager.broadcast_to_chat(
                    processed_message,
                    exclude_user_id=user_id,
                )
                logger.info(f"Message broadcasted to chat {processed_message.chat_id}")

        except WebSocketDisconnect:
            logger.info(f"User {user_id} disconnected")
            websocket_manager.disconnect(user_id)

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from user {user_id}")
            await websocket.send_text(
                json.dumps({
                    "error": "Invalid JSON format",
                }),
            )

        except Exception as e:
            logger.error(f"Error processing message from user {user_id}: {e!s}", exc_info=True)
            await websocket.send_text(
                json.dumps({
                    "error": str(e),
                }),
            )
            raise

    finally:
        logger.info(f"Cleaning up connection for user {user_id}")
        websocket_manager.disconnect(user_id)
