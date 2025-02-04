import asyncio
import json
import logging
from datetime import UTC, datetime

import websockets

logger = logging.getLogger(__name__)
async def client_session(user_id: int, chat_id: int, messages: list[str]):
    """Имитация сессии клиента"""
    uri = f"ws://localhost:8000/ws/{user_id}"

    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"User {user_id} connected")

            for msg in messages:
                # Формируем и отправляем сообщение
                message = {
                    "type": "message",
                    "chat_id": chat_id,
                    "content": msg,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                await websocket.send(json.dumps(message))
                logger.info(f"User {user_id} sent: {msg}")

                # Получаем ответ
                response = await websocket.recv()
                logger.info(f"User {user_id} received: {response}")

                # Небольшая пауза между сообщениями
                await asyncio.sleep(1)

            # Ждем некоторое время, чтобы увидеть ответы на последние сообщения
            await asyncio.sleep(2)

    except websockets.exceptions.ConnectionClosedError as e:
        logger.error(f"WebSocket connection closed for user {user_id}: {e!s}")
        raise
    except Exception as e:
        logger.error(f"Error in client session for user {user_id}: {e!s}")
        raise


async def test_chat():
    """Тестирование обмена сообщениями между пользователями"""
    try:
        # Тестовые сообщения
        alice_messages = [
            "Привет, Bob!",
            "Как дела?",
            "Что нового?",
        ]

        bob_messages = [
            "Привет, Alice!",
            "Все хорошо!",
            "Работаю над проектом",
        ]

        # Запускаем сессии параллельно
        await asyncio.gather(
            client_session(1, 1, alice_messages),  # Alice
            client_session(2, 1, bob_messages),  # Bob
        )

        logger.info("Chat test completed successfully")

    except Exception as e:
        logger.error(f"Chat test failed: {e!s}")
        raise


if __name__ == "__main__":
    logger.info("Starting WebSocket test")
    asyncio.run(test_chat())
