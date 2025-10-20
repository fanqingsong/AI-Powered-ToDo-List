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
    model_with_tools = _llm.bind_tools(_task_tools.get_tool_definitions())
    response = await model_with_tools.ainvoke(messages)
    return {"messages": response}


async def run_tools(input, config, **kwargs):
    """运行工具"""
    tool_node = ToolNode(_task_tools.get_tools())
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