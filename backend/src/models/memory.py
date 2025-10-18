from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MemoryType(str, Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    CONTEXT = "context"
    KNOWLEDGE = "knowledge"


class ContextType(str, Enum):
    CREATION = "creation"
    UPDATE = "update"
    DELETION = "deletion"
    QUERY = "query"


class ShortTermMemory(BaseModel):
    """短期记忆模型（会话级别）"""
    id: Optional[int] = None
    session_id: str
    user_id: Optional[str] = None
    message_type: MessageType
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LongTermMemory(BaseModel):
    """长期记忆模型（跨会话）"""
    id: Optional[int] = None
    user_id: Optional[str] = None
    memory_type: MemoryType
    key: str
    value: str
    importance_score: int = 1  # 1-10
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TaskContextMemory(BaseModel):
    """任务上下文记忆模型"""
    id: Optional[int] = None
    session_id: str
    task_id: Optional[int] = None
    context_type: ContextType
    context_data: Dict[str, Any]
    created_at: Optional[datetime] = None


class MemorySearchRequest(BaseModel):
    """记忆搜索请求"""
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    query: Optional[str] = None
    limit: int = 10


class MemorySearchResult(BaseModel):
    """记忆搜索结果"""
    memories: list[ShortTermMemory | LongTermMemory]
    total_count: int
    search_query: Optional[str] = None


class ConversationMessage(BaseModel):
    """会话消息模型"""
    id: Optional[int] = None
    session_id: str
    user_id: Optional[str] = None
    role: str  # 'user', 'assistant', 'system'
    content: str
    message_order: int
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


class ConversationHistory(BaseModel):
    """会话历史模型"""
    session_id: str
    user_id: Optional[str] = None
    messages: List[ConversationMessage] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ConversationRequest(BaseModel):
    """会话请求模型"""
    session_id: str
    user_id: Optional[str] = None
    message: str
    metadata: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """会话响应模型"""
    session_id: str
    message: ConversationMessage
    conversation_history: List[ConversationMessage] = []
