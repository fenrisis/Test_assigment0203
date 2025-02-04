import json
from datetime import UTC, datetime
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession, async_session
from starlette.websockets import WebSocketDisconnect


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
   try:
       message_data = WebSocketMessage(**data)
       logger.info(f"Processing message from user {user_id}: {data}")

       chat = await chat_service.get_chat(message_data.chat_id)
       if user_id not in [p.id for p in chat.participants]:
           logger.warning(f"User {user_id} attempted to access chat {message_data.chat_id} without permission")
           raise ValueError("User is not a participant of this chat")

       if message_data.type == "message":
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
       raise

async def websocket_endpoint(
   websocket: WebSocket,
   user_id: int
):
   await websocket.accept()

   async with async_session() as session:
       message_service = MessageService(session)
       chat_service = ChatService(session)

       try:
           user_chats = await chat_service.get_user_chats(user_id)
           await websocket_manager.connect(websocket, user_id)

           for chat in user_chats:
               websocket_manager.add_user_to_chat(user_id, chat.id)

           while True:
               data = await websocket.receive_text()
               message_data = json.loads(data)

               processed_message = await handle_websocket_message(
                   message_data,
                   user_id,
                   message_service,
                   chat_service,
               )

               await websocket.send_text(
                   json.dumps({
                       "event": "message",
                       "data": processed_message.model_dump(),
                       "timestamp": datetime.now(UTC).isoformat()
                   })
               )

               await websocket_manager.broadcast_to_chat(
                   processed_message,
                   exclude_user_id=user_id,
               )

       except WebSocketDisconnect:
           websocket_manager.disconnect(user_id)
           logger.info(f"User {user_id} disconnected")
