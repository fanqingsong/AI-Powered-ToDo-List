import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Annotated, TypedDict
# 移除LangChain消息对象的导入，使用字典格式
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode, create_react_agent
from langgraph.graph.message import add_messages
try:
    from langgraph.checkpoint.postgres import PostgresSaver
    from langchain_postgres import PostgresChatMessageHistory
except ImportError as e:
    print(f"Warning: Could not import PostgreSQL checkpointer: {e}")
    PostgresSaver = None
    PostgresChatMessageHistory = None
from ..services import TaskService
from ..services.memory_service import MemoryService
from ..services.conversation_service import ConversationService
from ..services.auth_service import AuthService
from ..models import ChatMessage, Role
from .tools import TaskTools
from .postgres_config import get_postgres_connection_string, get_postgres_store
from .checkpointer import get_postgres_checkpointer
from .llm_config import get_llm, is_llm_available
from .prompt_config import SYSTEM_PROMPT, ERROR_MESSAGES, SUCCESS_MESSAGES, DEBUG_MESSAGES


class TaskManagementAgent:
    """基于 LangGraph 的任务管理 Agent"""
    
    def __init__(self, task_service: TaskService):
        self.task_service = task_service
        self.memory_service = MemoryService()
        self.conversation_service = ConversationService()
        self.auth_service = AuthService()
        self.llm = self._init_llm()
        self.checkpointer = self._init_checkpointer()
        self.store = self._init_store()
        self.graph = self._build_graph()
    
    def _init_llm(self) -> ChatOpenAI:
        """初始化 LLM"""
        return get_llm()
    
    def _init_checkpointer(self):
        """初始化PostgreSQL checkpointer"""
        try:
            # 使用官方的 PostgresSaver
            checkpointer = get_postgres_checkpointer(get_postgres_connection_string())
            print(SUCCESS_MESSAGES["checkpointer_initialized"])
            return checkpointer
        except Exception as e:
            print(DEBUG_MESSAGES["checkpointer_init_failed"].format(error=e))
            return None
    
    def _init_store(self):
        """初始化PostgreSQL store"""
        if PostgresChatMessageHistory is None:
            print("PostgresChatMessageHistory 不可用，将使用内存模式")
            return None
        try:
            store = get_postgres_store()
            if store:
                print(SUCCESS_MESSAGES["store_initialized"])
            else:
                print(DEBUG_MESSAGES["store_init_failed"])
            return store
        except Exception as e:
            print(DEBUG_MESSAGES["store_init_error"].format(error=e))
            return None
    
    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 工作流"""
        
        # 创建工具实例
        task_tools = TaskTools(self.task_service)
        tools = task_tools.get_tools()
        
        # 构建自定义工作流
        tool_node = ToolNode(tools)
        
        # 创建绑定工具的 LLM
        llm_with_tools = self.llm.bind_tools(tools)
        
        def call_model(state: MessagesState) -> Dict[str, Any]:
            """调用模型"""
            messages = state["messages"]
            response = llm_with_tools.invoke(messages)
            return {"messages": [response]}
        
        def should_continue(state: MessagesState) -> str:
            """决定是否继续执行工具"""
            messages = state["messages"]
            last_message = messages[-1]
            
            # 如果最后一条消息有工具调用，则执行工具
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            
            # 否则结束
            return END
        
        # 构建图
        workflow = StateGraph(MessagesState)
        
        # 添加节点
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", tool_node)
        
        # 设置入口点
        workflow.set_entry_point("agent")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                END: END
            }
        )
        
        # 工具执行后返回给 agent
        workflow.add_edge("tools", "agent")
        
        # 编译图，使用checkpointer
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def process_message(
        self, 
        message: str, 
        conversation_history: List[ChatMessage] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> ChatMessage:
        """处理用户消息
        
        Args:
            message: 当前用户消息
            conversation_history: 对话历史，用于提供上下文（已废弃，现在从数据库加载）
            session_id: 会话ID，用于checkpointer和store
            user_id: 用户ID，用于会话关联
        """

        print(f"[DEBUG] 开始处理消息，message: {message}, session_id: {session_id}, user_id: {user_id}")
        print(f"[DEBUG] 开始处理消息，conversation_history: {conversation_history}")

        # 设置任务工具的用户ID
        if user_id and user_id.isdigit():
            # 重新构建图以设置用户ID
            task_tools = TaskTools(self.task_service)
            task_tools.set_user_id(int(user_id))
            tools = task_tools.get_tools()
            
            # 重新构建图
            tool_node = ToolNode(tools)
            llm_with_tools = self.llm.bind_tools(tools)
            
            def call_model(state: MessagesState) -> Dict[str, Any]:
                """调用模型"""
                messages = state["messages"]
                response = llm_with_tools.invoke(messages)
                return {"messages": [response]}
            
            def should_continue(state: MessagesState) -> str:
                """决定是否继续执行工具"""
                messages = state["messages"]
                last_message = messages[-1]
                
                # 如果最后一条消息有工具调用，则执行工具
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    return "tools"
                
                # 否则结束
                return END
            
            # 构建图
            workflow = StateGraph(MessagesState)
            
            # 添加节点
            workflow.add_node("agent", call_model)
            workflow.add_node("tools", tool_node)
            
            # 设置入口点
            workflow.set_entry_point("agent")
            
            # 添加条件边
            workflow.add_conditional_edges(
                "agent",
                should_continue,
                {
                    "tools": "tools",
                    END: END
                }
            )
            
            # 工具执行后返回给 agent
            workflow.add_edge("tools", "agent")
            
            # 更新图
            self.graph = workflow.compile(checkpointer=self.checkpointer)

        try:
            # 生成会话ID（如果没有提供）
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # 检查是否有可用的 LLM
            if not self._is_llm_available():
                return ChatMessage(
                    role=Role.ASSISTANT,
                    content=ERROR_MESSAGES["llm_unavailable"]
                )
            
            # 从数据库加载会话历史
            db_conversation_history = await self.conversation_service.get_conversation_history(
                session_id=session_id,
                limit=20,
                user_id=user_id
            )
            
            # 获取用户基本信息
            user_info = ""
            if user_id:
                try:
                    # 只有当user_id是数字字符串时才尝试获取用户信息
                    # 如果user_id是session_id（如test_session_001），则跳过用户信息获取
                    if user_id.isdigit():
                        user = await self.auth_service.get_user_by_id(int(user_id))
                        if user:
                            user_info = f"""
当前登录用户信息：
- 用户ID: {user.id}
- 用户名: {user.username}
- 显示名称: {user.display_name}
- 邮箱: {user.email}
- 注册时间: {user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else '未知'}
- 最后登录: {user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else '未知'}
- 账户状态: {'活跃' if user.is_active else '非活跃'}
"""
                    else:
                        # user_id是session_id，用户未登录
                        user_info = f"""
当前用户状态：未登录用户（会话ID: {user_id}）
"""
                except Exception as e:
                    print(f"获取用户信息失败: {e}")
            
            # 构建消息历史
            messages = [
                {"type": "system", "content": SYSTEM_PROMPT}
            ]
            
            # 如果有用户信息，添加到系统消息中
            if user_info:
                messages.append({
                    "type": "system", 
                    "content": f"{user_info}\n\n基于这些用户信息，你可以提供个性化的服务和建议。"
                })
            
            # 添加数据库中的对话历史
            for db_msg in db_conversation_history:
                messages.append({"type": db_msg.role, "content": db_msg.content})
            
            # 如果传入了conversation_history（向后兼容），也添加进去
            if conversation_history:
                for chat_msg in conversation_history:
                    if chat_msg.role == Role.USER:
                        messages.append({"type": "user", "content": chat_msg.content})
                    elif chat_msg.role == Role.ASSISTANT:
                        messages.append({"type": "assistant", "content": chat_msg.content})
            
            # 添加当前消息
            messages.append({"type": "user", "content": message})

            print(f"[DEBUG] 即将调用 LangGraph，messages 内容如下：\n{messages}")

            # 执行图，不使用checkpointer避免异步问题
            config = {
                "configurable": {"thread_id": session_id},
                "recursion_limit": 10  # 降低递归限制
            }

            result = await self.graph.ainvoke({"messages": messages}, config=config)
            
            # 获取最后一条消息
            last_message = result["messages"][-1]
            
            # 如果是工具调用结果，需要再次调用模型获取最终回复
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                # 添加工具结果到消息历史
                messages.extend(result["messages"][-2:])  # 添加工具调用和结果
                
                # 再次调用模型获取最终回复
                final_result = await self.graph.ainvoke({"messages": messages}, config=config)
                last_message = final_result["messages"][-1]
            
            # 创建响应消息
            response_message = ChatMessage(
                role=Role.ASSISTANT,
                content=last_message.content
            )
            
            # 保存对话到会话历史数据库
            try:
                await self.conversation_service.save_conversation_turn(
                    session_id=session_id,
                    user_message=message,
                    assistant_response=last_message.content,
                    user_id=user_id,
                    metadata={"agent": "langgraph", "timestamp": datetime.utcnow().isoformat()}
                )
                print(SUCCESS_MESSAGES["conversation_saved"].format(session_id=session_id))
            except Exception as e:
                print(DEBUG_MESSAGES["conversation_save_failed"].format(error=e))
                import traceback
                traceback.print_exc()
                # 不影响主要功能，继续返回响应
            
            return response_message
            
        except Exception as e:
            print(f"Error processing message: {e}")
            import traceback
            traceback.print_exc()
            # 检查是否是连接错误，如果是则提供降级模式提示
            error_msg = str(e)
            if "404" in error_msg or "Connection error" in error_msg or "Resource not found" in error_msg:
                return ChatMessage(
                    role=Role.ASSISTANT,
                    content=ERROR_MESSAGES["connection_error"]
                )
            else:
                return ChatMessage(
                    role=Role.ASSISTANT,
                    content=ERROR_MESSAGES["general_error"].format(error_msg=error_msg)
                )
    
    def _is_llm_available(self) -> bool:
        """检查 LLM 是否可用"""
        return is_llm_available()
    
    async def cleanup(self):
        """清理资源"""
        pass
