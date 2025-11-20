"""
SQLAlchemy ORM models for the chat_ai schema.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    __table_args__ = {"schema": "chat_ai"}
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.getdate(), nullable=False)
    is_active = Column(Boolean, server_default="1", nullable=False)
    
    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    """Session model for session-based authentication."""
    __tablename__ = "sessions"
    __table_args__ = {"schema": "chat_ai"}
    
    session_id = Column(String(64), primary_key=True)
    user_id = Column(Integer, ForeignKey("chat_ai.users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.getdate(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")


class Conversation(Base):
    """Conversation model to group related messages."""
    __tablename__ = "conversations"
    __table_args__ = {"schema": "chat_ai"}
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("chat_ai.users.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=func.getdate(), nullable=False, index=True)
    updated_at = Column(DateTime, server_default=func.getdate(), onupdate=func.getdate(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Message model for chat messages."""
    __tablename__ = "messages"
    __table_args__ = {"schema": "chat_ai"}
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("chat_ai.conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.getdate(), nullable=False, index=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class AgentConfig(Base):
    __tablename__ = "agents"
    __table_args__ = {"schema": "chat_ai"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200), nullable=True)
    system_prompt = Column(Text, nullable=False)
    model = Column(String(100), nullable=True)
    db_uri = Column(String(500), nullable=True)
    schema_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, server_default="1", nullable=False)
    tool_names = Column(Text, nullable=True)
