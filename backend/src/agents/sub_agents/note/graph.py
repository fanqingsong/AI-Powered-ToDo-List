"""
Note子Agent Graph
专门处理笔记管理相关的操作
"""

from typing import Dict, Any
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from ...supervisor.state import SupervisorState
from .tools import NoteTools
from .prompt import get_note_agent_prompt
from ...llmconf import get_llm


# 全局变量存储工具和LLM实例
_note_tools = None
_llm = None


async def call_model(state: SupervisorState, config: Dict[str, Any] = None):
    """调用模型"""
    if config is None:
        config = {}
    tool_definitions = _note_tools.get_tool_definitions()
    system_prompt = get_note_agent_prompt(tool_definitions)
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    model_with_tools = _llm.bind_tools(tool_definitions)
    response = await model_with_tools.ainvoke(messages)
    return {"messages": response}


async def run_tools(state: SupervisorState, config: Dict[str, Any] = None):
    """运行工具"""
    if config is None:
        config = {}
    # 从state中获取user_id并设置到工具中
    user_id = state.get("user_id")
    if user_id is not None and _note_tools:
        _note_tools.set_user_id(user_id)
    # 创建 ToolNode 并直接调用，不传递 config（ToolNode 不需要 config）
    tool_node = ToolNode(_note_tools.get_tools())
    return await tool_node.ainvoke(state)


def should_continue(state: SupervisorState):
    """决定是否继续执行工具"""
    messages = state["messages"]
    if not messages:
        return END
    last_message = messages[-1]
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return END
    return "tools"


# 在文件末尾直接构建graph
_llm = get_llm()
_note_tools = NoteTools()

# 构建Note子Agent的LangGraph
workflow = StateGraph(SupervisorState)

# 添加节点
workflow.add_node("agent", call_model)
workflow.add_node("tools", run_tools)

# 设置入口点
workflow.set_entry_point("agent")

# 添加条件边
workflow.add_conditional_edges(
    "agent",
    should_continue,
    ["tools", END]
)

# 添加边
workflow.add_edge("tools", "agent")

# 编译graph
graph = workflow.compile()

