from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index, func, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func as sql_func
from ..database import Base
import enum


class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class TaskDB(Base):
    """任务数据库模型"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    is_complete = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # 可选：关联用户
    created_at = Column(DateTime(timezone=True), server_default=sql_func.now())
    updated_at = Column(DateTime(timezone=True), server_default=sql_func.now(), onupdate=sql_func.now())
    
    __table_args__ = (
        Index('idx_tasks_user_id', 'user_id'),
        Index('idx_tasks_created_at', 'created_at'),
        Index('idx_tasks_is_complete', 'is_complete'),
    )


class ShortTermMemoryDB(Base):
    """短期记忆数据库模型"""
    __tablename__ = "short_term_memory"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    message_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    message_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=sql_func.now())
    updated_at = Column(DateTime(timezone=True), server_default=sql_func.now(), onupdate=sql_func.now())
    
    __table_args__ = (
        Index('idx_short_term_memory_session_id', 'session_id'),
        Index('idx_short_term_memory_user_id', 'user_id'),
        Index('idx_short_term_memory_created_at', 'created_at'),
    )


class LongTermMemoryDB(Base):
    """长期记忆数据库模型"""
    __tablename__ = "long_term_memory"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    memory_type = Column(String(50), nullable=False, index=True)
    key = Column(String(255), nullable=False, index=True)
    value = Column(Text, nullable=False)
    importance_score = Column(Integer, default=1, index=True)
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime(timezone=True), server_default=sql_func.now())
    created_at = Column(DateTime(timezone=True), server_default=sql_func.now())
    updated_at = Column(DateTime(timezone=True), server_default=sql_func.now(), onupdate=sql_func.now())
    
    __table_args__ = (
        Index('idx_long_term_memory_user_id', 'user_id'),
        Index('idx_long_term_memory_key', 'key'),
        Index('idx_long_term_memory_type', 'memory_type'),
        Index('idx_long_term_memory_importance', 'importance_score'),
    )


class TaskContextMemoryDB(Base):
    """任务上下文记忆数据库模型"""
    __tablename__ = "task_context_memory"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    task_id = Column(Integer, nullable=True, index=True)
    context_type = Column(String(50), nullable=False)
    context_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=sql_func.now())
    
    __table_args__ = (
        Index('idx_task_context_memory_session_id', 'session_id'),
        Index('idx_task_context_memory_task_id', 'task_id'),
    )


class ConversationHistoryDB(Base):
    """会话历史数据库模型"""
    __tablename__ = "conversation_history"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    message_order = Column(Integer, nullable=False)  # 消息在会话中的顺序
    message_metadata = Column(JSONB, nullable=True)  # 重命名避免与SQLAlchemy的metadata冲突
    created_at = Column(DateTime(timezone=True), server_default=sql_func.now())
    
    __table_args__ = (
        Index('idx_conversation_history_session_id', 'session_id'),
        Index('idx_conversation_history_user_id', 'user_id'),
        Index('idx_conversation_history_created_at', 'created_at'),
        Index('idx_conversation_history_session_order', 'session_id', 'message_order'),
    )


class UserDB(Base):
    """用户数据库模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=sql_func.now())
    updated_at = Column(DateTime(timezone=True), server_default=sql_func.now(), onupdate=sql_func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index('idx_users_username', 'username'),
        Index('idx_users_email', 'email'),
        Index('idx_users_created_at', 'created_at'),
    )


class UserSessionDB(Base):
    """用户会话数据库模型"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    session_name = Column(String(100), nullable=True)  # 用户自定义会话名称
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=sql_func.now())
    updated_at = Column(DateTime(timezone=True), server_default=sql_func.now(), onupdate=sql_func.now())
    last_activity = Column(DateTime(timezone=True), server_default=sql_func.now())
    
    __table_args__ = (
        Index('idx_user_sessions_user_id', 'user_id'),
        Index('idx_user_sessions_session_id', 'session_id'),
        Index('idx_user_sessions_created_at', 'created_at'),
        Index('idx_user_sessions_last_activity', 'last_activity'),
    )
