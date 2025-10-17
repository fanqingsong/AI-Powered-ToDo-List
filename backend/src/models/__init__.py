from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

# 导入记忆相关模型
try:
    from .memory import *
except ImportError as e:
    print(f"Warning: Could not import memory models: {e}")
    # 定义基本的记忆相关类以避免导入错误
    from enum import Enum
    from typing import Optional, List, Dict, Any
    from datetime import datetime
    
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

class TaskItem(BaseModel):
    id: int
    title: str
    isComplete: bool


class TaskCreateRequest(BaseModel):
    title: str
    isComplete: Optional[bool] = False


class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    isComplete: Optional[bool] = None


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    role: Role
    content: str


class ChatRequest(BaseModel):
    message: str
    sessionId: Optional[str] = None
    userId: Optional[str] = None
    conversation_history: Optional[List[ChatMessage]] = None
