from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union, Literal
from datetime import datetime
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


# Assistant-UI 相关模型
class LanguageModelTextPart(BaseModel):
    type: Literal["text"]
    text: str
    providerMetadata: Optional[Any] = None

class LanguageModelImagePart(BaseModel):
    type: Literal["image"]
    image: str  # Will handle URL or base64 string
    mimeType: Optional[str] = None
    providerMetadata: Optional[Any] = None

class LanguageModelFilePart(BaseModel):
    type: Literal["file"]
    data: str  # URL or base64 string
    mimeType: str
    providerMetadata: Optional[Any] = None

class LanguageModelToolCallPart(BaseModel):
    type: Literal["tool-call"]
    toolCallId: str
    toolName: str
    args: Any
    providerMetadata: Optional[Any] = None

class LanguageModelToolResultContentPart(BaseModel):
    type: Literal["text", "image"]
    text: Optional[str] = None
    data: Optional[str] = None
    mimeType: Optional[str] = None

class LanguageModelToolResultPart(BaseModel):
    type: Literal["tool-result"]
    toolCallId: str
    toolName: str
    result: Any
    isError: Optional[bool] = None
    content: Optional[List[LanguageModelToolResultContentPart]] = None
    providerMetadata: Optional[Any] = None

class LanguageModelSystemMessage(BaseModel):
    role: Literal["system"]
    content: str

class LanguageModelUserMessage(BaseModel):
    role: Literal["user"]
    content: List[Union[LanguageModelTextPart, LanguageModelImagePart, LanguageModelFilePart]]

class LanguageModelAssistantMessage(BaseModel):
    role: Literal["assistant"]
    content: List[Union[LanguageModelTextPart, LanguageModelToolCallPart]]

class LanguageModelToolMessage(BaseModel):
    role: Literal["tool"]
    content: List[LanguageModelToolResultPart]

LanguageModelV1Message = Union[
    LanguageModelSystemMessage,
    LanguageModelUserMessage,
    LanguageModelAssistantMessage,
    LanguageModelToolMessage,
]

class FrontendToolCall(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: dict[str, Any]

class ChatRequest(BaseModel):
    message: str
    sessionId: Optional[str] = None
    userId: Optional[str] = None
    conversation_history: Optional[List[ChatMessage]] = None
    frontend_tools_config: Optional[List[Dict[str, Any]]] = None

# Assistant-UI 聊天请求
class AssistantUIChatRequest(BaseModel):
    system: Optional[str] = ""
    tools: Optional[List[FrontendToolCall]] = []
    messages: List[LanguageModelV1Message]


# 导出会话历史相关模型
try:
    from .memory import ConversationMessage, ConversationHistory, ConversationRequest, ConversationResponse
except ImportError:
    # 如果导入失败，定义基本类
    class ConversationMessage(BaseModel):
        id: Optional[int] = None
        session_id: str
        user_id: Optional[str] = None
        role: str
        content: str
        message_order: int
        metadata: Optional[Dict[str, Any]] = None
        created_at: Optional[datetime] = None
    
    class ConversationHistory(BaseModel):
        session_id: str
        user_id: Optional[str] = None
        messages: List[ConversationMessage] = []
        created_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None
    
    class ConversationRequest(BaseModel):
        session_id: str
        user_id: Optional[str] = None
        message: str
        metadata: Optional[Dict[str, Any]] = None
    
    class ConversationResponse(BaseModel):
        session_id: str
        message: ConversationMessage
        conversation_history: List[ConversationMessage] = []

# 导出认证相关模型
try:
    from .auth import *
except ImportError:
    pass
