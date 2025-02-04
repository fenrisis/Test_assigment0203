
import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)


Base = declarative_base()


from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

chat_users = Table(
    "chat_users",
    Base.metadata,
    Column("chat_id", Integer, ForeignKey("chats.id", ondelete="CASCADE")),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    chats = relationship("Chat", secondary=chat_users, back_populates="participants")


class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    participants = relationship("User", secondary=chat_users, back_populates="chats")
    messages = relationship("Message", back_populates="chat", order_by="Message.timestamp")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])



DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/test_chat0203"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_users(session: AsyncSession) -> list[User]:
    """Создание тестовых пользователей"""
    users = [
        User(username="alice"),
        User(username="bob"),
    ]
    for user in users:
        session.add(user)
    await session.commit()
    logger.info(f"Created users: Alice (id={users[0].id}), Bob (id={users[1].id})")
    return users


async def create_chat(session: AsyncSession, users: list[User]) -> Chat:
    """Создание тестового чата между пользователями"""
    chat = Chat(participants=users)
    session.add(chat)
    await session.commit()
    logger.info(f"Created chat with id={chat.id}")
    return chat


async def create_messages(session: AsyncSession, chat: Chat, users: list[User]) -> list[Message]:
    """Создание тестовой переписки между пользователями"""
    base_time = datetime.now(UTC)

    conversation = [
        # Диалог с интервалом в 1 минуту между сообщениями
        (users[0], users[1], "Привет, Bob!", timedelta(minutes=0)),
        (users[1], users[0], "Привет, Alice!", timedelta(minutes=1)),
        (users[0], users[1], "Как дела?", timedelta(minutes=2)),
        (users[1], users[0], "Все хорошо!", timedelta(minutes=3)),
        (users[0], users[1], "Что нового?", timedelta(minutes=4)),
        (users[1], users[0], "Работаю над проектом", timedelta(minutes=5)),
    ]

    messages = []
    for sender, receiver, text, time_offset in conversation:
        message = Message(
            text=text,
            chat_id=chat.id,
            sender_id=sender.id,
            receiver_id=receiver.id,
            timestamp=base_time + time_offset,
        )
        session.add(message)
        messages.append(message)
        logger.debug(f"Created message: {sender.username} -> {receiver.username}: {text}")

    await session.commit()
    logger.info(f"Created {len(messages)} messages in chat {chat.id}")
    return messages


async def create_test_data():
    """Создание тестовых данных для чата"""
    logger.info("Starting test data creation")

    try:
        # Пересоздаем все таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables recreated")

        async with async_session() as session:
            # Создаем тестовые данные
            users = await create_users(session)
            chat = await create_chat(session, users)
            messages = await create_messages(session, chat, users)

            logger.info("\nTest data creation completed successfully")
            logger.info("WebSocket test endpoints:")
            logger.info(f"ws://localhost:8000/ws/{users[0].id}  # Connect as Alice")
            logger.info(f"ws://localhost:8000/ws/{users[1].id}  # Connect as Bob")
            logger.info("\nREST API endpoint:")
            logger.info(f"GET http://localhost:8000/api/history/{chat.id}")

    except Exception as e:
        logger.error(f"Error creating test data: {e!s}")
        raise


if __name__ == "__main__":
    asyncio.run(create_test_data())
