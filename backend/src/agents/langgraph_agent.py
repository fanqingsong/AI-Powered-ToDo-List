import os
from typing import Dict, List, Any, Optional, Annotated, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from ..services import TaskService
from ..models import ChatMessage, Role


class TaskManagementAgent:
    """基于 LangGraph 的任务管理 Agent"""
    
    def __init__(self, task_service: TaskService):
        self.task_service = task_service
        self.llm = self._init_llm()
        self.graph = self._build_graph()
    
    def _init_llm(self) -> ChatOpenAI:
        """初始化 LLM"""
        # 支持多种 LLM 提供商
        if os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_ENDPOINT"):
            # Azure OpenAI 配置
            return ChatOpenAI(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"),
                temperature=0.1,
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                base_url=f"{os.getenv('AZURE_OPENAI_ENDPOINT')}openai/deployments/{os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o-mini')}/",
                default_query={"api-version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")}
            )
        elif os.getenv("OPENAI_API_KEY"):
            # 标准 OpenAI API
            return ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.1,
                api_key=os.getenv("OPENAI_API_KEY")
            )
        elif os.getenv("ANTHROPIC_API_KEY"):
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model="claude-3-sonnet-20240229",
                temperature=0.1,
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        else:
            # 使用本地模型或默认配置
            return ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.1,
                api_key="dummy-key"  # 将使用模拟响应
            )
    
    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 工作流"""
        
        # 定义工具
        @tool
        async def create_task(title: str, isComplete: bool = False) -> str:
            """创建新任务
            
            Args:
                title: 任务标题
                isComplete: 任务是否完成，默认为 False
                
            Returns:
                任务创建结果信息
            """
            task = await self.task_service.add_task(title, isComplete)
            return f'任务创建成功: "{task.title}" (ID: {task.id})'
        
        @tool
        async def get_tasks() -> str:
            """获取所有任务
            
            Returns:
                任务列表信息
            """
            tasks = await self.task_service.get_all_tasks()
            if not tasks:
                return '没有找到任务。'
            
            task_list = '\n'.join([
                f'- {t.id}: {t.title} ({"已完成" if t.isComplete else "未完成"})'
                for t in tasks
            ])
            return f'找到 {len(tasks)} 个任务:\n{task_list}'
        
        @tool
        async def get_task(id: int) -> str:
            """获取指定任务
            
            Args:
                id: 任务ID
                
            Returns:
                任务信息
            """
            task = await self.task_service.get_task_by_id(id)
            if not task:
                return f'未找到 ID 为 {id} 的任务。'
            
            status = "已完成" if task.isComplete else "未完成"
            return f'任务 {task.id}: "{task.title}" - 状态: {status}'
        
        @tool
        async def update_task(id: int, title: Optional[str] = None, isComplete: Optional[bool] = None) -> str:
            """更新任务
            
            Args:
                id: 任务ID
                title: 新标题（可选）
                isComplete: 新完成状态（可选）
                
            Returns:
                更新结果信息
            """
            updated = await self.task_service.update_task(id, title, isComplete)
            if not updated:
                return f'未找到 ID 为 {id} 的任务。'
            return f'任务 {id} 更新成功。'
        
        @tool
        async def delete_task(id: int) -> str:
            """删除任务
            
            Args:
                id: 任务ID
                
            Returns:
                删除结果信息
            """
            deleted = await self.task_service.delete_task(id)
            if not deleted:
                return f'未找到 ID 为 {id} 的任务。'
            return f'任务 {id} 删除成功。'
        
        # 创建工具列表
        tools = [create_task, get_tasks, get_task, update_task, delete_task]
        tool_node = ToolNode(tools)
        
        # 定义状态
        class AgentState(TypedDict):
            messages: Annotated[List[Any], add_messages]
        
        # 创建绑定工具的 LLM
        llm_with_tools = self.llm.bind_tools(tools)
        
        def call_model(state: AgentState) -> Dict[str, Any]:
            """调用模型"""
            messages = state["messages"]
            response = llm_with_tools.invoke(messages)
            return {"messages": [response]}
        
        def should_continue(state: AgentState) -> str:
            """决定是否继续执行工具"""
            messages = state["messages"]
            last_message = messages[-1]
            # 如果最后一条消息有工具调用，则执行工具
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            # 否则结束
            return END
        
        # 构建图
        workflow = StateGraph(AgentState)
        
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
        
        return workflow.compile()
    
    async def process_message(self, message: str) -> ChatMessage:
        """处理用户消息"""
        try:
            # 检查是否有可用的 LLM
            if not self._is_llm_available():
                return ChatMessage(
                    role=Role.ASSISTANT,
                    content="抱歉，AI 功能当前不可用。请配置以下任一环境变量以启用 AI 功能：\n\n• Azure OpenAI: AZURE_OPENAI_API_KEY 和 AZURE_OPENAI_ENDPOINT\n• 标准 OpenAI: OPENAI_API_KEY\n• Anthropic: ANTHROPIC_API_KEY\n\n您仍然可以使用以下功能：\n- 查看任务列表\n- 创建新任务\n- 更新任务状态\n- 删除任务"
                )
            
            # 构建消息
            messages = [
                SystemMessage(content="""你是一个任务管理助手。你可以帮助用户：
1. 创建新任务
2. 查看所有任务
3. 查看特定任务
4. 更新任务（标题或完成状态）
5. 删除任务

请根据用户的需求，使用相应的工具来帮助他们管理任务。如果用户没有明确说明要做什么，请询问他们需要什么帮助。

请用中文回复用户。"""),
                HumanMessage(content=message)
            ]
            
            # 执行图
            result = await self.graph.ainvoke({"messages": messages})
            
            # 获取最后一条消息
            last_message = result["messages"][-1]
            
            # 如果是工具调用结果，需要再次调用模型获取最终回复
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                # 添加工具结果到消息历史
                messages.extend(result["messages"][-2:])  # 添加工具调用和结果
                
                # 再次调用模型获取最终回复
                final_result = await self.graph.ainvoke({"messages": messages})
                last_message = final_result["messages"][-1]
            
            return ChatMessage(
                role=Role.ASSISTANT,
                content=last_message.content
            )
            
        except Exception as e:
            print(f"Error processing message: {e}")
            # 检查是否是连接错误，如果是则提供降级模式提示
            error_msg = str(e)
            if "404" in error_msg or "Connection error" in error_msg or "Resource not found" in error_msg:
                return ChatMessage(
                    role=Role.ASSISTANT,
                    content="抱歉，AI 功能当前不可用。请配置以下任一环境变量以启用 AI 功能：\n\n• Azure OpenAI: AZURE_OPENAI_API_KEY 和 AZURE_OPENAI_ENDPOINT\n• 标准 OpenAI: OPENAI_API_KEY\n• Anthropic: ANTHROPIC_API_KEY\n\n您仍然可以使用以下功能：\n- 查看任务列表\n- 创建新任务\n- 更新任务状态\n- 删除任务"
                )
            else:
                return ChatMessage(
                    role=Role.ASSISTANT,
                    content=f"抱歉，处理您的消息时出现了错误：{error_msg}"
                )
    
    def _is_llm_available(self) -> bool:
        """检查 LLM 是否可用"""
        return bool(
            os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_ENDPOINT") or
            os.getenv("OPENAI_API_KEY") or 
            os.getenv("ANTHROPIC_API_KEY")
        )
    
    async def cleanup(self):
        """清理资源"""
        pass
