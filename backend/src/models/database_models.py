from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index, func, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func as sql_func
from ..database import Base
import enum


class UserRole(enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


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


class ScheduleDB(Base):
    """日程安排数据库模型"""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    is_all_day = Column(Boolean, default=False)
    location = Column(String(255), nullable=True)
    color = Column(String(7), default="#1890ff")  # 颜色代码，默认蓝色
    created_at = Column(DateTime(timezone=True), server_default=sql_func.now())
    updated_at = Column(DateTime(timezone=True), server_default=sql_func.now(), onupdate=sql_func.now())
    
    __table_args__ = (
        Index('idx_schedules_user_id', 'user_id'),
        Index('idx_schedules_start_time', 'start_time'),
        Index('idx_schedules_end_time', 'end_time'),
        Index('idx_schedules_user_start', 'user_id', 'start_time'),
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


class NoteCategory(enum.Enum):
    """笔记分类枚举"""
    PERSONAL = "PERSONAL"  # 个人笔记
    WORK = "WORK"  # 工作笔记
    STUDY = "STUDY"  # 学习笔记
    IDEA = "IDEA"  # 想法笔记
    MEETING = "MEETING"  # 会议笔记
    OTHER = "OTHER"  # 其他


class NoteDB(Base):
    """笔记数据库模型"""
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(Enum(NoteCategory, name='notecategory'), default=NoteCategory.PERSONAL, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    tags = Column(JSONB, nullable=True)  # 标签数组，存储为JSON
    is_pinned = Column(Boolean, default=False, index=True)  # 是否置顶
    is_archived = Column(Boolean, default=False, index=True)  # 是否归档
    word_count = Column(Integer, default=0)  # 字数统计
    last_accessed = Column(DateTime(timezone=True), server_default=sql_func.now())  # 最后访问时间
    created_at = Column(DateTime(timezone=True), server_default=sql_func.now())
    updated_at = Column(DateTime(timezone=True), server_default=sql_func.now(), onupdate=sql_func.now())
    
    __table_args__ = (
        Index('idx_notes_user_id', 'user_id'),
        Index('idx_notes_category', 'category'),
        Index('idx_notes_is_pinned', 'is_pinned'),
        Index('idx_notes_is_archived', 'is_archived'),
        Index('idx_notes_created_at', 'created_at'),
        Index('idx_notes_updated_at', 'updated_at'),
        Index('idx_notes_user_category', 'user_id', 'category'),
        Index('idx_notes_user_pinned', 'user_id', 'is_pinned'),
    )
