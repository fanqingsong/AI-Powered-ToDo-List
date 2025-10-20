from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, AsyncGenerator
import json
from ..models import (
    TaskItem, TaskCreateRequest, TaskUpdateRequest, ChatRequest, ChatMessage, 
    ConversationMessage, ConversationHistory, AssistantUIChatRequest, 
    LanguageModelV1Message, FrontendToolCall
)
from ..services import TaskService, ConversationService
from ..agents import TaskAgent
from ..auth.dependencies import get_current_active_user, get_optional_current_user
from ..models.auth import User


def create_api_routes(
    task_service: TaskService,
    task_agent: TaskAgent,
    conversation_service: ConversationService
) -> APIRouter:
    """
    Create API router with task CRUD endpoints and chat agent routes.
    
    Routes:
    - GET    /tasks          : Retrieves all tasks
    - POST   /tasks          : Creates a new task
    - GET    /tasks/{id}     : Retrieves a task by its ID
    - PUT    /tasks/{id}     : Updates a task by its ID
    - DELETE /tasks/{id}     : Deletes a task by its ID
    - POST   /chat/langgraph : Processes a chat message using the LangGraph agent
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
        "/chat/stream",
        operation_id="streamChat",
        description="流式处理聊天消息，支持实时响应"
    )
    async def stream_chat(
        chat_request: ChatRequest,
        current_user: User = Depends(get_optional_current_user)
    ):
        """流式处理聊天消息"""
        try:
            if not chat_request.message:
                raise HTTPException(status_code=400, detail="Message is required")
            
            # 如果用户已登录，使用用户ID，否则使用sessionId作为临时用户标识
            # 优先使用前端传递的userId，然后是current_user，最后是sessionId
            if chat_request.userId and chat_request.userId.isdigit():
                user_id = chat_request.userId
            elif current_user:
                user_id = str(current_user.id)
            else:
                user_id = chat_request.sessionId
            
            print(f"[DEBUG] 流式聊天认证状态: current_user={current_user}, user_id={user_id}, chat_request.userId={chat_request.userId}")
            
            async def generate_stream() -> AsyncGenerator[str, None]:
                """生成流式响应"""
                try:
                    # 发送用户消息
                    yield f"data: {json.dumps({'type': 'user', 'content': chat_request.message})}\n\n"
                    
                    # 处理消息并流式返回
                    async for chunk in task_agent.process_message_stream(
                        chat_request.message,
                        chat_request.conversation_history,
                        chat_request.sessionId,
                        user_id,
                        chat_request.frontend_tools_config
                    ):
                        yield f"data: {json.dumps(chunk)}\n\n"
                    
                    # 发送结束标记
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    
                except Exception as e:
                    print(f"Error in stream generation: {e}")
                    error_chunk = {
                        'type': 'error',
                        'content': f'处理消息时出错: {str(e)}'
                    }
                    yield f"data: {json.dumps(error_chunk)}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in stream chat: {e}")
            raise HTTPException(status_code=500, detail="Failed to process stream message")
    
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
            
            # 设置用户ID到任务代理
            if current_user:
                task_agent.set_user_id(current_user.id)
            
            async def run(controller: RunController):
                tool_calls = {}
                tool_calls_by_idx = {}
                
                async for msg, metadata in task_agent.assistant_ui_graph.astream(
                    {"messages": inputs},
                    {
                        "configurable": {
                            "system": request.system,
                            "frontend_tools": request.tools,
                        }
                    },
                    stream_mode="messages",
                ):
                    if isinstance(msg, ToolMessage):
                        if msg.tool_call_id in tool_calls:
                            tool_controller = tool_calls[msg.tool_call_id]
                            tool_controller.set_result(msg.content)
                        else:
                            print(f"Warning: Tool call ID {msg.tool_call_id} not found in tool_calls")
                    
                    if isinstance(msg, AIMessageChunk) or isinstance(msg, AIMessage):
                        if msg.content:
                            controller.append_text(msg.content)
                        
                        for chunk in msg.tool_call_chunks:
                            if not chunk["index"] in tool_calls_by_idx:
                                tool_controller = await controller.add_tool_call(
                                    chunk["name"], chunk["id"]
                                )
                                tool_calls_by_idx[chunk["index"]] = tool_controller
                                tool_calls[chunk["id"]] = tool_controller
                            else:
                                tool_controller = tool_calls_by_idx[chunk["index"]]
                            
                            tool_controller.append_args_text(chunk["args"])
            
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
