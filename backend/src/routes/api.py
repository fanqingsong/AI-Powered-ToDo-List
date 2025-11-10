from fastapi import APIRouter, HTTPException, Depends
from typing import List, Any
import json
from datetime import datetime
from ..models import (
    TaskItem, TaskCreateRequest, TaskUpdateRequest, ChatMessage, 
    ConversationMessage, ConversationHistory, AssistantUIChatRequest, 
    LanguageModelV1Message, FrontendToolCall
)
from ..services import TaskService, ConversationService
from ..auth.dependencies import get_current_active_user, get_optional_current_user
from ..models.auth import User


def create_api_routes(
    task_service: TaskService,
    supervisor_graph: Any,  # LangGraph compiled graph
    conversation_service: ConversationService
) -> APIRouter:
    """
    Create API router with resource management endpoints (Tasks, Schedules, Notes) and chat agent routes.
    
    Routes:
    - GET    /tasks          : Retrieves all tasks
    - POST   /tasks          : Creates a new task
    - GET    /tasks/{id}     : Retrieves a task by its ID
    - PUT    /tasks/{id}     : Updates a task by its ID
    - DELETE /tasks/{id}     : Deletes a task by its ID
    - POST   /chat           : Processes a chat message using the LangGraph agent (Assistant-UI)
    """
    router = APIRouter()
    
    @router.get("/health", operation_id="healthCheck", include_in_schema=False)
    async def health_check():
        """Health check endpoint for Docker"""
        return {"status": "healthy", "service": "AI-Powered-ToDo-List"}
    
    @router.get(
        "/tasks",
        response_model=List[TaskItem],
        operation_id="getAllTasks",
        description="Retrieve all tasks in the task list."
    )
    async def get_all_tasks(current_user: User = Depends(get_optional_current_user)):
        """Get all tasks"""
        try:
            # 如果用户已登录，只获取该用户的任务；否则获取所有任务
            user_id = current_user.id if current_user else None
            tasks = await task_service.get_all_tasks(user_id)
            return tasks
        except Exception as e:
            print(f"Error getting tasks: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to get tasks: {str(e)}")
    
    @router.post(
        "/tasks",
        response_model=TaskItem,
        status_code=201,
        operation_id="createTask",
        description="Create a new task with a title and completion status."
    )
    async def create_task(task_request: TaskCreateRequest, current_user: User = Depends(get_optional_current_user)):
        """Create a new task"""
        try:
            if not task_request.title:
                raise HTTPException(status_code=400, detail="Title is required")
            
            # 如果用户已登录，关联到该用户；否则不关联用户
            user_id = current_user.id if current_user else None
            task = await task_service.add_task(
                task_request.title, 
                task_request.isComplete or False,
                user_id
            )
            return task
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error creating task: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")
    
    @router.get(
        "/tasks/{task_id}",
        response_model=TaskItem,
        operation_id="getTaskById",
        description="Retrieve a task by its unique ID."
    )
    async def get_task_by_id(task_id: int, current_user: User = Depends(get_optional_current_user)):
        """Get a task by its ID"""
        try:
            user_id = current_user.id if current_user else None
            task = await task_service.get_task_by_id(task_id, user_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            return task
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to get task")
    
    @router.put(
        "/tasks/{task_id}",
        response_model=TaskItem,
        operation_id="updateTask",
        description="Update a task's title or completion status by its ID."
    )
    async def update_task(task_id: int, task_request: TaskUpdateRequest, current_user: User = Depends(get_optional_current_user)):
        """Update a task by its ID"""
        try:
            user_id = current_user.id if current_user else None
            updated = await task_service.update_task(
                task_id, 
                task_request.title, 
                task_request.isComplete,
                user_id
            )
            if not updated:
                raise HTTPException(status_code=404, detail="Task not found")
            
            task = await task_service.get_task_by_id(task_id, user_id)
            return task
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to update task")
    
    @router.delete(
        "/tasks/{task_id}",
        operation_id="deleteTask",
        description="Delete a task by its unique ID."
    )
    async def delete_task(task_id: int, current_user: User = Depends(get_optional_current_user)):
        """Delete a task by its ID"""
        try:
            user_id = current_user.id if current_user else None
            deleted = await task_service.delete_task(task_id, user_id)
            if not deleted:
                raise HTTPException(status_code=404, detail="Task not found")
            return {"message": "Task deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to delete task")
    
    @router.post(
        "/chat",
        operation_id="assistantUIChat",
        description="Assistant-UI 聊天端点，支持前端工具调用"
    )
    async def assistant_ui_chat(
        request: AssistantUIChatRequest,
        current_user: User = Depends(get_optional_current_user)
    ):
        """Assistant-UI 聊天端点"""
        try:
            # 使用 assistant-stream 的 DataStreamResponse
            from assistant_stream import create_run, RunController
            from assistant_stream.serialization import DataStreamResponse
            from langchain_core.messages import (
                HumanMessage, AIMessageChunk, AIMessage, ToolMessage,
                SystemMessage, BaseMessage
            )
            
            def convert_to_langchain_messages(messages: List[LanguageModelV1Message]) -> List[BaseMessage]:
                result = []
                for msg in messages:
                    if msg.role == "system":
                        result.append(SystemMessage(content=msg.content))
                    elif msg.role == "user":
                        # 处理用户消息的内容列表
                        content = []
                        for p in msg.content:
                            if hasattr(p, 'type') and p.type == "text":
                                content.append({"type": "text", "text": p.text})
                            elif hasattr(p, 'type') and p.type == "image":
                                content.append({"type": "image_url", "image_url": p.image})
                        result.append(HumanMessage(content=content))
                    elif msg.role == "assistant":
                        # 处理助手消息的内容列表
                        text_parts = [
                            p for p in msg.content if hasattr(p, 'type') and p.type == "text"
                        ]
                        text_content = " ".join(p.text for p in text_parts)
                        tool_calls = [
                            {
                                "id": p.toolCallId,
                                "name": p.toolName,
                                "args": p.args,
                            }
                            for p in msg.content
                            if hasattr(p, 'type') and p.type == "tool-call"
                        ]
                        result.append(AIMessage(content=text_content, tool_calls=tool_calls))
                    elif msg.role == "tool":
                        # 处理工具消息
                        for tool_result in msg.content:
                            result.append(
                                ToolMessage(
                                    content=str(tool_result.result),
                                    tool_call_id=tool_result.toolCallId,
                                )
                            )
                return result
            
            inputs = convert_to_langchain_messages(request.messages)
            
            # 获取用户ID
            current_user_id = None
            if current_user:
                current_user_id = current_user.id
            
            # 构建初始状态，包含user_id
            initial_state = {
                "messages": inputs,
                "user_id": current_user_id,
                "plan": None,
                "current_step": 0,
                "execution_results": [],
                "selected_agent": None,
                "agent_context": {},
                "should_continue": True,
                "is_planning": False,
                "is_executing": False,
                "is_aggregating": False,
            }
            
            async def run(controller: RunController):
                tool_calls = {}
                tool_calls_by_idx = {}
                
                print(f"[DEBUG] Assistant-UI Chat: 开始处理请求，user_id={current_user_id}")
                
                # 使用 stream_mode="messages" 来流式传输消息
                # 配置参数
                config = {
                    "configurable": {
                        "system": request.system,
                        "frontend_tools": request.tools,
                        "thread_id": f"assistant_ui_{current_user_id or 'anonymous'}_{datetime.now().timestamp()}",
                    }
                }
                
                # stream_mode="messages" 可能返回单个消息对象或 (message, metadata) 元组
                async for event in supervisor_graph.astream(
                    initial_state,
                    config,
                    stream_mode="messages",
                ):
                    # 处理返回值：可能是单个消息对象或 (message, metadata) 元组
                    if isinstance(event, tuple) and len(event) == 2:
                        msg, metadata = event
                    else:
                        msg = event
                    
                    print(f"[DEBUG] Assistant-UI Chat: 收到消息类型={type(msg).__name__}, content={getattr(msg, 'content', 'N/A')[:100] if hasattr(msg, 'content') else 'N/A'}")
                    
                    # 处理工具消息
                    if isinstance(msg, ToolMessage):
                        print(f"[DEBUG] Assistant-UI Chat: 处理 ToolMessage, tool_call_id={msg.tool_call_id}")
                        if msg.tool_call_id in tool_calls:
                            tool_controller = tool_calls[msg.tool_call_id]
                            tool_controller.set_result(msg.content)
                        else:
                            print(f"[WARNING] Tool call ID {msg.tool_call_id} not found in tool_calls")
                    
                    # 处理 AI 消息（包括流式文本和工具调用）
                    if isinstance(msg, AIMessageChunk) or isinstance(msg, AIMessage):
                        content = msg.content if hasattr(msg, 'content') else None
                        
                        # 检查消息来源：通过消息的附加信息
                        node_name = ""
                        
                        # 发送所有 AI 消息的文本内容（包括 aggregate 节点的最终响应）
                        # 注意：这里会发送所有节点的消息，但只有 aggregate 节点有最终响应
                        if content:
                            # 检查是否是完整的消息（不是 chunk）
                            if isinstance(msg, AIMessage) and not isinstance(msg, AIMessageChunk):
                                print(f"[DEBUG] Assistant-UI Chat: 发送完整 AI 消息 (node={node_name}): {content[:100]}...")
                                controller.append_text(content)
                            elif isinstance(msg, AIMessageChunk):
                                # 流式发送 chunk
                                print(f"[DEBUG] Assistant-UI Chat: 发送 AI 消息 chunk (node={node_name}): {content[:50]}...")
                                controller.append_text(content)
                        
                        # 处理工具调用
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                            for tool_call in msg.tool_calls:
                                tool_call_id = tool_call.get("id") if isinstance(tool_call, dict) else getattr(tool_call, "id", None)
                                tool_name = tool_call.get("name") if isinstance(tool_call, dict) else getattr(tool_call, "name", None)
                                
                                if tool_call_id and tool_name:
                                    if tool_call_id not in tool_calls:
                                        tool_controller = await controller.add_tool_call(tool_name, tool_call_id)
                                        tool_calls[tool_call_id] = tool_controller
                                        
                                        # 添加工具参数
                                        tool_args = tool_call.get("args") if isinstance(tool_call, dict) else getattr(tool_call, "args", None)
                                        if tool_args:
                                            tool_controller.append_args_text(str(tool_args) if not isinstance(tool_args, str) else tool_args)
                                    else:
                                        # 如果工具调用已存在，更新参数
                                        tool_controller = tool_calls[tool_call_id]
                                        tool_args = tool_call.get("args") if isinstance(tool_call, dict) else getattr(tool_call, "args", None)
                                        if tool_args:
                                            tool_controller.append_args_text(str(tool_args) if not isinstance(tool_args, str) else tool_args)
                
                print(f"[DEBUG] Assistant-UI Chat: 处理完成")
            
            return DataStreamResponse(create_run(run))
            
        except Exception as e:
            print(f"Error in assistant UI chat: {e}")
            raise HTTPException(status_code=500, detail="Failed to process assistant UI chat")
    
    # 会话历史管理端点
    @router.get(
        "/conversations/{session_id}",
        response_model=List[ConversationMessage],
        operation_id="getConversationHistory",
        description="获取指定会话的历史记录"
    )
    async def get_conversation_history(
        session_id: str, 
        user_id: str = None, 
        limit: int = 50,
        current_user: User = Depends(get_optional_current_user)
    ):
        """获取会话历史"""
        try:
            # 如果用户已登录，优先使用当前用户ID
            effective_user_id = str(current_user.id) if current_user else user_id
            
            messages = await conversation_service.get_conversation_history(
                session_id=session_id,
                limit=limit,
                user_id=effective_user_id
            )
            return messages
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            raise HTTPException(status_code=500, detail="Failed to get conversation history")
    
    @router.delete(
        "/conversations/{session_id}",
        operation_id="clearConversationHistory",
        description="清空指定会话的历史记录"
    )
    async def clear_conversation_history(session_id: str, user_id: str = None):
        """清空会话历史"""
        try:
            success = await conversation_service.clear_conversation_history(
                session_id=session_id,
                user_id=user_id
            )
            if success:
                return {"message": "Conversation history cleared successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to clear conversation history")
        except Exception as e:
            print(f"Error clearing conversation history: {e}")
            raise HTTPException(status_code=500, detail="Failed to clear conversation history")
    
    @router.get(
        "/conversations/stats/{session_id}",
        operation_id="getConversationStats",
        description="获取会话统计信息"
    )
    async def get_conversation_stats(session_id: str, user_id: str = None):
        """获取会话统计信息"""
        try:
            stats = await conversation_service.get_conversation_stats(
                session_id=session_id,
                user_id=user_id
            )
            return stats
        except Exception as e:
            print(f"Error getting conversation stats: {e}")
            raise HTTPException(status_code=500, detail="Failed to get conversation stats")
    
    @router.get(
        "/conversations/user/{user_id}",
        operation_id="getUserSessions",
        description="获取用户的所有会话"
    )
    async def get_user_sessions(user_id: str, limit: int = 20):
        """获取用户的所有会话"""
        try:
            sessions = await conversation_service.get_user_sessions(
                user_id=user_id,
                limit=limit
            )
            return sessions
        except Exception as e:
            print(f"Error getting user sessions: {e}")
            raise HTTPException(status_code=500, detail="Failed to get user sessions")
    
    # Assistant-UI 支持端点
    @router.post(
        "/chat/threads",
        operation_id="createThread",
        description="创建新的对话线程"
    )
    async def create_thread():
        """创建新的对话线程"""
        try:
            import uuid
            thread_id = str(uuid.uuid4())
            return {"thread_id": thread_id}
        except Exception as e:
            print(f"Error creating thread: {e}")
            raise HTTPException(status_code=500, detail="Failed to create thread")
    
    @router.get(
        "/chat/threads/{thread_id}/state",
        operation_id="getThreadState",
        description="获取线程状态"
    )
    async def get_thread_state(thread_id: str):
        """获取线程状态"""
        try:
            # 从数据库加载会话历史
            messages = await conversation_service.get_conversation_history(
                session_id=thread_id,
                limit=50
            )
            
            # 转换为 assistant-ui 格式
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            return {
                "messages": formatted_messages,
                "tasks": []
            }
        except Exception as e:
            print(f"Error getting thread state: {e}")
            raise HTTPException(status_code=500, detail="Failed to get thread state")
    
    return router
