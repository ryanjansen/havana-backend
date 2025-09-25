from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class ChatStatus(str, enum.Enum):
    AI = "ai"
    HUMAN = "human"
    HANDOVER_PENDING = "handover_pending"


class Sender(str, enum.Enum):
    USER = "user"
    AI = "ai"
    ADMIN = "admin"
    SYSTEM = "system"


class WSEvent(str, enum.Enum):
    NEW_MESSAGE = "new_message"
    ESCALATED = "escalated"
    CALL_BOOKED = "call_booked"


class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(ChatStatus), default=ChatStatus.AI)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    messages = relationship("Message", back_populates="chat")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    sender = Column(String)  # user | assistant | admin
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    chat = relationship("Chat", back_populates="messages")
