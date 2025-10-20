"""
Agent Graph

直接在顶层构建的 LangGraph 工作流
支持前端工具调用
"""

from typing import Dict, List, Any
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.errors import NodeInterrupt
from pydantic import BaseModel

from .tools import TaskTools
from .state import AgentState


class AnyArgsSchema(BaseModel):
    """允许任意参数的 Schema"""
    class Config:
        extra = "allow"


class FrontendTool(BaseTool):
    """前端工具类，用于处理前端工具调用"""
    
    def __init__(self, name: str):
        super().__init__(name=name, description="", args_schema=AnyArgsSchema)
    
    def _run(self, *args, **kwargs):
        raise NodeInterrupt("This is a frontend tool call")
    
    async def _arun(self, *args, **kwargs) -> str:
        raise NodeInterrupt("This is a frontend tool call")


def get_tool_definitions(task_tools: TaskTools, config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """获取工具定义，包括前端工具"""
    base_tools = task_tools.get_tool_definitions()
    
    if config and "configurable" in config and "frontend_tools" in config["configurable"]:
        frontend_tools = [
            {"type": "function", "function": tool.model_dump()}
            for tool in config["configurable"]["frontend_tools"]
        ]
        return base_tools + frontend_tools
    
    return base_tools


def get_tools(task_tools: TaskTools, config: Dict[str, Any] = None) -> List[BaseTool]:
    """获取工具实例，包括前端工具"""
    base_tools = task_tools.get_tools()
    
    if config and "configurable" in config and "frontend_tools" in config["configurable"]:
        frontend_tools = [
            FrontendTool(tool.name) for tool in config["configurable"]["frontend_tools"]
        ]
        return base_tools + frontend_tools
    
    return base_tools


# 全局变量用于存储 llm 和 task_tools
_llm = None
_task_tools = None


def set_llm_and_tools(llm: ChatOpenAI, task_tools: TaskTools):
    """设置全局的 llm 和 task_tools"""
    global _llm, _task_tools
    _llm = llm
    _task_tools = task_tools


async def call_model(state, config):
    """调用模型"""
    from langchain_core.messages import SystemMessage
    
    system = config["configurable"]["system"]
    messages = [SystemMessage(content=system)] + state["messages"]
    model_with_tools = _llm.bind_tools(get_tool_definitions(_task_tools, config))
    response = await model_with_tools.ainvoke(messages)
    return {"messages": response}


async def run_tools(input, config, **kwargs):
    """运行工具"""
    tool_node = ToolNode(get_tools(_task_tools, config))
    return await tool_node.ainvoke(input, config, **kwargs)


def should_continue(state):
    """决定是否继续执行工具"""
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return END
    else:
        return "tools"


# Define a new graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", run_tools)

# Set entry point
workflow.set_entry_point("agent")

# Add conditional edges
workflow.add_conditional_edges(
    "agent",
    should_continue,
    ["tools", END],
)

# Add edge
workflow.add_edge("tools", "agent")

# Compile the graph
graph = workflow.compile()