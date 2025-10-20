import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Annotated, TypedDict, AsyncGenerator
# 移除LangChain消息对象的导入，使用字典格式
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode, create_react_agent
from langgraph.graph.message import add_messages
from langgraph.errors import NodeInterrupt
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
        # 初始化任务工具
        self.task_tools = TaskTools(task_service)
        self.graph = self._build_graph()
        self.assistant_ui_graph = self._build_assistant_ui_graph()
    
    def set_user_id(self, user_id: int):
        """设置当前用户ID"""
        self.task_tools.set_user_id(user_id)
    
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
    
    def _build_graph(self, user_id: Optional[int] = None, frontend_tools_config: Optional[List[Dict[str, Any]]] = None) -> StateGraph:
        """构建 LangGraph 工作流
        
        Args:
            user_id: 用户ID，如果提供则设置到任务工具中
            frontend_tools_config: 前端工具配置
        """
        
        # 创建工具实例
        if user_id:
            task_tools = TaskTools()
            task_tools.set_user_id(user_id)
        else:
            task_tools = TaskTools(self.task_service)
        
        # 设置前端工具配置
        if frontend_tools_config:
            task_tools.set_frontend_tools_config(frontend_tools_config)
        
        tools = task_tools.get_tools()
        tool_definitions = task_tools.get_tool_definitions()
        
        # 构建自定义工作流
        tool_node = ToolNode(tools)
        
        # 创建绑定工具的 LLM
        llm_with_tools = self.llm.bind_tools(tool_definitions)
        
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
        
        async def run_tools_with_interrupt_handling(input_data: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
            """运行工具并处理前端工具中断"""
            try:
                return await tool_node.ainvoke(input_data, config)
            except NodeInterrupt as e:
                # 前端工具调用中断，返回特殊响应
                interrupt_message = str(e)
                print(f"[DEBUG] 前端工具中断: {interrupt_message}")
                
                # 解析前端工具调用信息
                if "Frontend tool call:" in interrupt_message:
                    tool_name = interrupt_message.split("Frontend tool call:")[-1].strip()
                    return {
                        "messages": [{
                            "type": "assistant",
                            "content": f"frontend_tool_call:{tool_name} 正在执行前端操作..."
                        }]
                    }
                
                # 其他中断情况
                return {
                    "messages": [{
                        "type": "assistant", 
                        "content": "前端工具调用已触发，请查看前端界面变化。"
                    }]
                }
        
        # 构建图
        workflow = StateGraph(MessagesState)
        
        # 添加节点
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", run_tools_with_interrupt_handling)
        
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
    
    def _build_assistant_ui_graph(self) -> StateGraph:
        """构建 Assistant-UI 专用的 LangGraph 工作流"""
        from langchain_core.tools import BaseTool
        from pydantic import BaseModel
        
        class AnyArgsSchema(BaseModel):
            class Config:
                extra = "allow"
        
        class FrontendTool(BaseTool):
            def __init__(self, name: str):
                super().__init__(name=name, description="", args_schema=AnyArgsSchema)
            
            def _run(self, *args, **kwargs):
                raise NodeInterrupt("This is a frontend tool call")
            
            async def _arun(self, *args, **kwargs) -> str:
                raise NodeInterrupt("This is a frontend tool call")
        
        def get_tool_defs(config):
            """获取工具定义，包括前端工具"""
            frontend_tools = [
                {"type": "function", "function": tool.model_dump()}
                for tool in config["configurable"]["frontend_tools"]
            ]
            return self.task_tools.get_tool_definitions() + frontend_tools
        
        def get_tools(config):
            """获取工具实例，包括前端工具"""
            frontend_tools = [
                FrontendTool(tool.name) for tool in config["configurable"]["frontend_tools"]
            ]
            return self.task_tools.get_tools() + frontend_tools
        
        async def call_model(state, config):
            """调用模型"""
            from langchain_core.messages import SystemMessage
            
            system = config["configurable"]["system"]
            messages = [SystemMessage(content=system)] + state["messages"]
            model_with_tools = self.llm.bind_tools(get_tool_defs(config))
            response = await model_with_tools.ainvoke(messages)
            return {"messages": response}
        
        async def run_tools(input, config, **kwargs):
            """运行工具"""
            tool_node = ToolNode(get_tools(config))
            return await tool_node.ainvoke(input, config, **kwargs)
        
        def should_continue(state):
            """决定是否继续执行工具"""
            messages = state["messages"]
            last_message = messages[-1]
            if not last_message.tool_calls:
                return END
            else:
                return "tools"
        
        # 构建工作流
        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", run_tools)
        
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            ["tools", END],
        )
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def _is_llm_available(self) -> bool:
        """检查 LLM 是否可用"""
        return is_llm_available()
    
    async def process_message_stream(
        self, 
        message: str, 
        conversation_history: List[ChatMessage] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        frontend_tools_config: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式处理用户消息
        
        Args:
            message: 当前用户消息
            conversation_history: 对话历史，用于提供上下文（已废弃，现在从数据库加载）
            session_id: 会话ID，用于checkpointer和store
            user_id: 用户ID，用于会话关联
            frontend_tools_config: 前端工具配置
            
        Yields:
            Dict[str, Any]: 流式响应数据块
        """
        import asyncio
        
        print(f"[DEBUG] 开始流式处理消息，message: {message}, session_id: {session_id}, user_id: {user_id}")

        try:
            # 生成会话ID（如果没有提供）
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # 检查是否有可用的 LLM
            if not self._is_llm_available():
                yield {
                    'type': 'error',
                    'content': ERROR_MESSAGES["llm_unavailable"]
                }
                return
            
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

            print(f"[DEBUG] 即将调用 LangGraph 流式处理，messages 内容如下：\n{messages}")

            # 设置任务工具的用户ID和前端工具配置
            if user_id and user_id.isdigit():
                # 重新构建图以设置用户ID和前端工具配置
                self.graph = self._build_graph(user_id=int(user_id), frontend_tools_config=frontend_tools_config)

            # 发送开始处理信号
            yield {
                'type': 'assistant',
                'content': '',
                'isStreaming': True
            }

            # 执行图，使用流式处理
            config = {
                "configurable": {"thread_id": session_id},
                "recursion_limit": 20
            }

            # 使用 astream 进行流式处理
            accumulated_content = ""
            async for chunk in self.graph.astream({"messages": messages}, config=config):
                if "agent" in chunk:
                    agent_messages = chunk["agent"]["messages"]
                    if agent_messages:
                        last_message = agent_messages[-1]
                        if hasattr(last_message, 'content') and last_message.content:
                            # 模拟流式输出，逐字符发送
                            content = last_message.content
                            if content != accumulated_content:
                                new_content = content[len(accumulated_content):]
                                accumulated_content = content
                                
                                # 发送内容块
                                yield {
                                    'type': 'assistant',
                                    'content': new_content,
                                    'isStreaming': True
                                }
                                
                                # 添加小延迟以模拟流式效果
                                await asyncio.sleep(0.05)
                
                elif "tools" in chunk:
                    # 工具调用结果
                    tool_messages = chunk["tools"]["messages"]
                    if tool_messages:
                        last_tool_message = tool_messages[-1]
                        if hasattr(last_tool_message, 'content') and last_tool_message.content:
                            content = last_tool_message.content
                            
                            # 检查是否是前端工具调用
                            if isinstance(content, str) and content.startswith("frontend_tool_call:"):
                                tool_name = content.split("frontend_tool_call:")[-1].strip()
                                yield {
                                    'type': 'frontend_tool',
                                    'tool_name': tool_name,
                                    'content': content,
                                    'isStreaming': True
                                }
                            else:
                                yield {
                                    'type': 'tool',
                                    'content': content,
                                    'isStreaming': True
                                }

            # 发送完成信号
            yield {
                'type': 'assistant',
                'content': '',
                'isStreaming': False
            }
            
            # 保存对话到会话历史数据库
            try:
                await self.conversation_service.save_conversation_turn(
                    session_id=session_id,
                    user_message=message,
                    assistant_response=accumulated_content,
                    user_id=user_id,
                    metadata={"agent": "langgraph_stream", "timestamp": datetime.utcnow().isoformat()}
                )
                print(SUCCESS_MESSAGES["conversation_saved"].format(session_id=session_id))
            except Exception as e:
                print(DEBUG_MESSAGES["conversation_save_failed"].format(error=e))
                import traceback
                traceback.print_exc()
            
        except Exception as e:
            print(f"Error in stream processing: {e}")
            import traceback
            traceback.print_exc()
            
            error_msg = str(e)
            if "404" in error_msg or "Connection error" in error_msg or "Resource not found" in error_msg:
                yield {
                    'type': 'error',
                    'content': ERROR_MESSAGES["connection_error"]
                }
            else:
                yield {
                    'type': 'error',
                    'content': ERROR_MESSAGES["general_error"].format(error_msg=error_msg)
                }
    
    async def cleanup(self):
        """清理资源"""
        pass
