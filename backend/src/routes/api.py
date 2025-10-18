from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models import TaskItem, TaskCreateRequest, TaskUpdateRequest, ChatRequest, ChatMessage, ConversationMessage, ConversationHistory
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
    - POST   /chat/foundry   : Processes a chat message using the LangGraph agent (legacy)
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
    async def get_all_tasks():
        """Get all tasks"""
        try:
            tasks = await task_service.get_all_tasks()
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
    async def create_task(task_request: TaskCreateRequest):
        """Create a new task"""
        try:
            if not task_request.title:
                raise HTTPException(status_code=400, detail="Title is required")
            
            task = await task_service.add_task(
                task_request.title, 
                task_request.isComplete or False
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
    async def get_task_by_id(task_id: int):
        """Get a task by its ID"""
        try:
            task = await task_service.get_task_by_id(task_id)
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
    async def update_task(task_id: int, task_request: TaskUpdateRequest):
        """Update a task by its ID"""
        try:
            updated = await task_service.update_task(
                task_id, 
                task_request.title, 
                task_request.isComplete
            )
            if not updated:
                raise HTTPException(status_code=404, detail="Task not found")
            
            task = await task_service.get_task_by_id(task_id)
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
    async def delete_task(task_id: int):
        """Delete a task by its ID"""
        try:
            deleted = await task_service.delete_task(task_id)
            if not deleted:
                raise HTTPException(status_code=404, detail="Task not found")
            return {"message": "Task deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to delete task")
    
    @router.post("/chat/foundry", response_model=ChatMessage, operation_id="chatWithFoundry", include_in_schema=False)
    async def chat_with_foundry(chat_request: ChatRequest):
        """Process a chat message using the LangGraph agent (legacy endpoint)"""
        try:
            if not chat_request.message:
                raise HTTPException(status_code=400, detail="Message is required")
            
            response = await task_agent.process_message(
                chat_request.message, 
                chat_request.conversation_history
            )
            return response
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in LangGraph chat: {e}")
            raise HTTPException(status_code=500, detail="Failed to process message")
    
    @router.post("/chat/langgraph", response_model=ChatMessage, operation_id="chatWithLangGraph", include_in_schema=False)
    async def chat_with_langgraph(
        chat_request: ChatRequest,
        current_user: User = Depends(get_optional_current_user)
    ):
        """Process a chat message using the LangGraph agent"""
        try:
            if not chat_request.message:
                raise HTTPException(status_code=400, detail="Message is required")
            
            # 如果用户已登录，使用用户ID，否则使用sessionId作为临时用户标识
            user_id = str(current_user.id) if current_user else chat_request.sessionId
            
            response = await task_agent.process_message(
                chat_request.message, 
                chat_request.conversation_history,
                chat_request.sessionId,
                user_id
            )
            return response
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in LangGraph chat: {e}")
            raise HTTPException(status_code=500, detail="Failed to process message")
    
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
    
    return router
