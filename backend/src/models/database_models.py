from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func as sql_func
from ..database import Base


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
