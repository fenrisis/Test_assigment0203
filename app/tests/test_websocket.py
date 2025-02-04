import asyncio
import json
import logging
from datetime import UTC, datetime

import websockets

logger = logging.getLogger(__name__)


async def client_session(user_id: int, chat_id: int, messages: list[str]):
    """Simulate a client session"""
    uri = f"ws://localhost:8000/ws/{user_id}"

    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"User {user_id} connected")

            for msg in messages:
                # Format and send message
                message = {
                    "type": "message",
                    "chat_id": chat_id,
                    "content": msg,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                await websocket.send(json.dumps(message))
                logger.info(f"User {user_id} sent: {msg}")

                # Get response
                response = await websocket.recv()
                logger.info(f"User {user_id} received: {response}")

                # Small delay between messages
                await asyncio.sleep(1)

            # Wait to see responses to last messages
            await asyncio.sleep(2)

    except websockets.exceptions.ConnectionClosedError as e:
        logger.error(f"WebSocket connection closed for user {user_id}: {e!s}")
        raise
    except Exception as e:
        logger.error(f"Error in client session for user {user_id}: {e!s}")
        raise


async def test_chat():
    """Test message exchange between users"""
    try:
        # WebSocket chat should be the second chat (id=2)
        chat_id = 2  # Hardcoded because we know the order of creation

        # Test messages
        alice_messages = [
            "Hi, Bob!",
            "How are you?",
            "What's new?",
        ]

        bob_messages = [
            "Hi, Alice!",
            "I'm good!",
            "Working on a project",
        ]

        # Run sessions in parallel
        await asyncio.gather(
            client_session(1, chat_id, alice_messages),  # Alice
            client_session(2, chat_id, bob_messages),  # Bob
        )

        logger.info("Chat test completed successfully")

    except Exception as e:
        logger.error(f"Chat test failed: {e!s}")
        raise


if __name__ == "__main__":
    logger.info("Starting WebSocket test")
    asyncio.run(test_chat())