# app/tests/fixtures/data.py
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat
from app.models.message import Message
from app.models.user import User


async def create_test_data(session: AsyncSession):
    """Создание тестовых данных"""
    # Создаем тестовых пользователей
    users = [
        User(username="alice"),
        User(username="bob"),
        User(username="charlie"),
        User(username="david"),
    ]

    for user in users:
        session.add(user)
    await session.commit()

    # Создаем тестовые чаты
    chats = [
        # Чат между Alice и Bob
        Chat(
            participants=[users[0], users[1]],  # Alice и Bob
            created_at=datetime.now(UTC),
        ),
        # Чат между Alice и Charlie
        Chat(
            participants=[users[0], users[2]],  # Alice и Charlie
            created_at=datetime.now(UTC),
        ),
        # Чат между Bob и David
        Chat(
            participants=[users[1], users[3]],  # Bob и David
            created_at=datetime.now(UTC),
        ),
    ]

    for chat in chats:
        session.add(chat)
    await session.commit()

    # Создаем тестовые сообщения
    messages = [
        # Сообщения в чате Alice и Bob
        Message(
            text="Привет, Bob!",
            chat_id=chats[0].id,
            sender_id=users[0].id,  # От Alice
            receiver_id=users[1].id,  # Для Bob
            created_at=datetime.now(UTC),
        ),
        Message(
            text="Привет, Alice!",
            chat_id=chats[0].id,
            sender_id=users[1].id,  # От Bob
            receiver_id=users[0].id,  # Для Alice
            created_at=datetime.now(UTC),
        ),
        Message(
            text="Как дела?",
            chat_id=chats[0].id,
            sender_id=users[0].id,  # От Alice
            receiver_id=users[1].id,  # Для Bob
            created_at=datetime.now(UTC),
        ),

        # Сообщения в чате Alice и Charlie
        Message(
            text="Привет, Charlie!",
            chat_id=chats[1].id,
            sender_id=users[0].id,  # От Alice
            receiver_id=users[2].id,  # Для Charlie
            created_at=datetime.now(UTC),
        ),
        Message(
            text="Привет, Alice! Что нового?",
            chat_id=chats[1].id,
            sender_id=users[2].id,  # От Charlie
            receiver_id=users[0].id,  # Для Alice
            created_at=datetime.now(UTC),
        ),

        # Сообщения в чате Bob и David
        Message(
            text="Привет, David!",
            chat_id=chats[2].id,
            sender_id=users[1].id,  # От Bob
            receiver_id=users[3].id,  # Для David
            created_at=datetime.now(UTC),
        ),
        Message(
            text="Привет, Bob! Как дела?",
            chat_id=chats[2].id,
            sender_id=users[3].id,  # От David
            receiver_id=users[1].id,  # Для Bob
            created_at=datetime.now(UTC),
        ),
    ]

    for message in messages:
        session.add(message)
    await session.commit()

    return {
        "users": users,
        "chats": chats,
        "messages": messages,
    }
