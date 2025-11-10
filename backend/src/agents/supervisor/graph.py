"""
Supervisor Graph
构建完整的supervisor工作流
"""

import json
import re
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from .state import SupervisorState, ExecutionPlan, ExecutionStep, ExecutionResult
from .prompt import get_plan_node_prompt, get_aggregate_node_prompt, get_intent_classify_prompt
from ..sub_agents.task.graph import graph as task_graph
from ..sub_agents.schedule.graph import graph as schedule_graph
from ..sub_agents.note.graph import graph as note_graph
from ..llmconf import get_llm
from ..dbconf import get_postgres_connection_string, get_postgres_store, get_postgres_checkpointer


# 全局变量存储supervisor相关实例
_llm = None
_checkpointer = None
_store = None


def _extract_user_message(state: SupervisorState) -> str:
    """从状态中提取用户消息"""
    if state.get("messages"):
        for msg in state["messages"]:
            if hasattr(msg, 'content') and isinstance(msg, HumanMessage):
                return msg.content
    return state.get("agent_context", {}).get("user_message", "")


async def _intent_classify_node(state: SupervisorState, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """意图分类节点 - 判断用户请求是否需要调用业务数据"""
    if config is None:
        config = {}
    if _llm is None:
        raise RuntimeError("LLM not initialized.")
    
    # 获取用户消息
    user_message = _extract_user_message(state)
    
    # 确保 user_message 是字符串类型
    if not user_message or not isinstance(user_message, str):
        # 如果没有用户消息，默认需要业务数据（保守策略）
        return {
            "needs_business_data": True,
            "is_planning": True
        }
    
    # 第一层：硬编码规则 - 检查常见的简单问候和对话
    # 这些情况明确不需要业务数据
    user_message_lower = user_message.lower().strip()
    
    # 简单问候列表
    simple_greetings = [
        "hi", "hello", "hey", "嗨", "你好", "您好",
        "早上好", "下午好", "晚上好", "good morning", "good afternoon", "good evening",
        "再见", "拜拜", "bye", "goodbye", "see you",
        "谢谢", "thanks", "thank you", "不客气", "you're welcome",
        "ok", "好的", "知道了", "明白", "了解",
        "help", "帮助", "你能做什么", "有什么功能"
    ]
    
    # 检查是否是简单问候（完全匹配或只包含问候词）
    if user_message_lower in simple_greetings:
        print(f"[DEBUG] 意图分类：检测到简单问候 '{user_message}'，直接返回不需要业务数据")
        return {
            "needs_business_data": False,
            "is_planning": False
        }
    
    # 检查是否只包含问候词（去除标点和空格后）
    message_clean = re.sub(r'[^\w\u4e00-\u9fff]', '', user_message_lower)
    if message_clean in simple_greetings:
        print(f"[DEBUG] 意图分类：检测到简单问候（清理后）'{message_clean}'，直接返回不需要业务数据")
        return {
            "needs_business_data": False,
            "is_planning": False
        }
    
    # 第二层：使用LLM判断（对于不明确的请求）
    system_prompt = get_intent_classify_prompt()
    
    # 调用LLM判断意图
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"用户请求：{user_message}\n\n请判断是否需要调用业务数据（只返回JSON）：")
    ]
    
    response = await _llm.ainvoke(messages)
    intent_text = response.content if hasattr(response, 'content') else str(response)
    
    # 解析判断结果
    try:
        # 尝试提取JSON
        if "```json" in intent_text:
            intent_text = intent_text.split("```json")[1].split("```")[0].strip()
        elif "```" in intent_text:
            intent_text = intent_text.split("```")[1].split("```")[0].strip()
        
        intent_dict = json.loads(intent_text)
        needs_business_data = intent_dict.get("needs_business_data", False)  # 默认为False，保守策略（避免误判）
        
        print(f"[DEBUG] 意图分类：LLM判断结果 - needs_business_data={needs_business_data}, reason={intent_dict.get('reason', 'N/A')}")
        
        # 额外检查：如果LLM判断为true，但消息很短且不包含明确的业务关键词，强制设为false
        if needs_business_data and len(user_message.strip()) < 10:
            # 检查是否包含明确的业务关键词
            business_keywords = ["任务", "日程", "笔记", "task", "schedule", "note", "添加", "创建", "查看", "删除", "更新"]
            has_business_keyword = any(keyword in user_message for keyword in business_keywords)
            
            if not has_business_keyword:
                print(f"[DEBUG] 意图分类：消息过短且无业务关键词，强制设为不需要业务数据")
                needs_business_data = False
        
    except Exception as e:
        # 如果解析失败，使用保守策略：默认不需要业务数据（避免误判）
        print(f"[WARNING] 意图分类解析失败: {e}, 使用默认策略（不需要业务数据）")
        needs_business_data = False
    
    return {
        "needs_business_data": needs_business_data,
        "is_planning": needs_business_data  # 如果需要业务数据，进入planning阶段
    }


async def _simple_response_node(state: SupervisorState, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """简单回复节点 - 处理不需要业务数据的简单对话"""
    if config is None:
        config = {}
    if _llm is None:
        raise RuntimeError("LLM not initialized.")
    
    user_message = _extract_user_message(state)
    
    # 使用LLM生成友好的回复
    system_prompt = """你是一个友好的AI助手。用户发送了简单的问候或咨询，请用中文生成一个友好、简洁的回复。
    
你可以：
- 回应问候
- 介绍系统功能
- 提供帮助建议
- 进行简单的对话

请保持回复简洁、友好，不要超过2-3句话。"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"用户消息：{user_message}\n\n请生成友好的回复：")
    ]
    
    response = await _llm.ainvoke(messages)
    reply = response.content if hasattr(response, 'content') else str(response)
    
    return {
        "messages": [AIMessage(content=reply)],
        "should_continue": False
    }


async def _plan_node(state: SupervisorState, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """规划节点 - 分析用户意图，制定执行计划"""
    if config is None:
        config = {}
    if _llm is None:
        raise RuntimeError("LLM not initialized.")
    
    system_prompt = get_plan_node_prompt()
    
    # 获取用户消息
    user_message = ""
    if state.get("messages"):
        for msg in state["messages"]:
            if hasattr(msg, 'content') and isinstance(msg, HumanMessage):
                user_message = msg.content
                break
    
    if not user_message:
        # 如果没有用户消息，从状态中获取
        user_message = state.get("agent_context", {}).get("user_message", "")
    
    # 调用LLM生成计划
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"用户请求：{user_message}\n\n请生成执行计划（只返回JSON）：")
    ]
    
    response = await _llm.ainvoke(messages)
    plan_text = response.content if hasattr(response, 'content') else str(response)
    
    # 解析计划
    try:
        # 尝试提取JSON
        if "```json" in plan_text:
            plan_text = plan_text.split("```json")[1].split("```")[0].strip()
        elif "```" in plan_text:
            plan_text = plan_text.split("```")[1].split("```")[0].strip()
        
        plan_dict = json.loads(plan_text)
        plan: ExecutionPlan = {
            "summary": plan_dict.get("summary", ""),
            "steps": plan_dict.get("steps", [])
        }
    except Exception as e:
        # 如果解析失败，创建默认计划
        print(f"[WARNING] 计划解析失败: {e}, 使用默认计划")
        plan: ExecutionPlan = {
            "summary": "无法解析计划，使用默认处理",
            "steps": [{
                "agent": "task",
                "action": "query",
                "params": {},
                "description": "处理用户请求"
            }]
        }
    
    return {
        "plan": plan,
        "current_step": 0,
        "is_planning": False,
        "is_executing": True,
        "execution_results": []
    }


async def _route_node(state: SupervisorState, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """路由节点 - 根据计划选择下一个要执行的子agent"""
    if config is None:
        config = {}
    
    plan = state.get("plan")
    current_step = state.get("current_step", 0)
    
    if not plan or not plan.get("steps"):
        return {
            "selected_agent": None,
            "should_continue": False,
            "is_executing": False,
            "is_aggregating": True
        }
    
    steps = plan["steps"]
    if current_step >= len(steps):
        # 所有步骤执行完成
        return {
            "selected_agent": None,
            "should_continue": False,
            "is_executing": False,
            "is_aggregating": True
        }
    
    # 获取当前步骤
    step = steps[current_step]
    selected_agent = step.get("agent")
    step_description = step.get("description", "")
    
    # 准备子agent的上下文
    agent_context = {
        "action": step.get("action"),
        "params": step.get("params", {}),
        "description": step_description,
        "user_message": _extract_user_message(state)
    }
    
    # 为子agent准备指令消息
    # 子agent需要从messages中获取指令，所以我们创建一个包含当前步骤指令的HumanMessage
    instruction_message = HumanMessage(content=step_description)
    
    return {
        "selected_agent": selected_agent,
        "agent_context": agent_context,
        "messages": [instruction_message],  # 为子agent设置指令消息
        "should_continue": True
    }


async def _execute_node(state: SupervisorState, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """执行节点 - 记录子agent的执行结果并更新状态
    
    注意：子agent的实际执行已经在graph层的子agent节点中完成，
    这个节点负责从messages中提取子agent的最终响应并记录到execution_results中
    """
    if config is None:
        config = {}
    
    selected_agent = state.get("selected_agent")
    current_step = state.get("current_step", 0)
    
    # 从messages中提取子agent的最终响应
    # 子agent执行后，messages中会包含工具调用和最终响应
    execution_result_text = ""
    messages = state.get("messages", [])
    
    if messages:
        # 从后往前查找最后一个AIMessage（子agent的最终响应）
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                # 获取AI消息的内容
                if hasattr(msg, 'content') and msg.content:
                    execution_result_text = str(msg.content)
                    break
                # 如果没有content，检查是否有tool_calls的结果
                elif hasattr(msg, 'tool_calls') and msg.tool_calls:
                    # 如果有工具调用，查找对应的ToolMessage
                    for tool_call in msg.tool_calls:
                        tool_call_id = tool_call.get("id") if isinstance(tool_call, dict) else getattr(tool_call, "id", None)
                        if tool_call_id:
                            # 查找对应的ToolMessage
                            for tool_msg in messages:
                                if isinstance(tool_msg, ToolMessage) and hasattr(tool_msg, "tool_call_id"):
                                    if tool_msg.tool_call_id == tool_call_id:
                                        execution_result_text = str(tool_msg.content) if hasattr(tool_msg, "content") else str(tool_msg)
                                        break
                break
    
    # 如果仍然没有找到结果，尝试从agent_context获取（向后兼容）
    if not execution_result_text:
        agent_context = state.get("agent_context", {})
        execution_result_text = agent_context.get("execution_result", "")
    
    # 如果没有执行结果，说明子agent可能没有执行或执行失败
    if not execution_result_text:
        execution_result_text = "执行未完成或失败"
    
    # 判断执行是否成功
    is_success = "失败" not in execution_result_text and "错误" not in execution_result_text and "未完成" not in execution_result_text
    
    # 记录执行结果
    execution_result: ExecutionResult = {
        "step_index": current_step,
        "agent": selected_agent,
        "success": is_success,
        "result": execution_result_text,
        "error": None if is_success else execution_result_text
    }
    
    execution_results = state.get("execution_results", [])
    execution_results.append(execution_result)
    
    # 移动到下一步
    return {
        "execution_results": execution_results,
        "current_step": current_step + 1,
        "selected_agent": None
    }


async def _aggregate_node(state: SupervisorState, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """汇总节点 - 汇总所有执行结果，生成最终响应"""
    if config is None:
        config = {}
    if _llm is None:
        raise RuntimeError("LLM not initialized.")
    
    plan = state.get("plan")
    execution_results = state.get("execution_results", [])
    
    # 构建汇总消息
    summary_parts = []
    if plan:
        summary_parts.append(f"执行计划：{plan.get('summary', '')}")
    
    if execution_results:
        summary_parts.append("\n执行结果：")
        for result in execution_results:
            status = "✓" if result.get("success") else "✗"
            summary_parts.append(
                f"{status} [{result.get('agent')}] {result.get('result', '')}"
            )
    
    # 使用LLM生成友好的最终响应
    system_prompt = get_aggregate_node_prompt()
    
    user_message = _extract_user_message(state)
    summary_text = "\n".join(summary_parts)
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"用户原始请求：{user_message}\n\n{summary_text}\n\n请生成友好的响应：")
    ]
    
    response = await _llm.ainvoke(messages)
    final_response = response.content if hasattr(response, 'content') else str(response)
    
    return {
        "messages": [AIMessage(content=final_response)],
        "is_aggregating": False,
        "should_continue": False
    }


def _intent_decision(state: SupervisorState) -> str:
    """意图决策函数 - 根据意图分类结果路由到plan或simple_response"""
    needs_business_data = state.get("needs_business_data", True)
    
    if needs_business_data:
        return "plan"  # 需要业务数据，进入plan节点
    else:
        return "simple_response"  # 不需要业务数据，直接回复


def _route_decision(state: SupervisorState) -> str:
    """路由决策函数"""
    selected_agent = state.get("selected_agent")
    should_continue = state.get("should_continue", False)
    
    if not should_continue:
        return "aggregate"
    
    if selected_agent == "task":
        return "task_agent"
    elif selected_agent == "schedule":
        return "schedule_agent"
    elif selected_agent == "note":
        return "note_agent"
    else:
        return "aggregate"


# 在文件末尾直接构建graph
_llm = get_llm()

# 初始化checkpointer和store
try:
    _checkpointer = get_postgres_checkpointer(get_postgres_connection_string())
    print("[SUCCESS] Supervisor Graph checkpointer 初始化成功")
except Exception as e:
    print(f"[WARNING] Supervisor Graph checkpointer 初始化失败: {e}")
    _checkpointer = None

try:
    _store = get_postgres_store()
    if _store:
        print("[SUCCESS] Supervisor Graph store 初始化成功")
    else:
        print("[WARNING] Supervisor Graph store 初始化失败，将使用内存模式")
except Exception as e:
    print(f"[WARNING] Supervisor Graph store 初始化失败: {e}")
    _store = None

# ===================== Supervisor工作流图拓扑结构 =====================
#
#       ┌────────────────────┐
#       │  intent_classify   │   # 0. 意图分类（判断是否需要业务数据）
#       └─────────┬──────────┘
#                 │
#        ┌────────┴────────┐
#        │                 │
#        ▼                 ▼
#   ┌─────────┐    ┌────────────────────┐
#   │ simple  │    │  supervisor_plan   │   # 1. 生成执行计划
#   │response │    └─────────┬──────────┘
#   └────┬────┘              │
#        │                   ▼
#        │          ┌────────────────────┐
#        │          │ supervisor_route   │   # 2. 路由到对应子Agent
#        │          └────────────────────┘
#        │         /    |      |     |   \
#        │        ▼     ▼      ▼     ▼    ▼
#        │    task  schedule  note  aggregate END
#        │   agent  agent     agent
#        │     │      │        │      │
#        │     ▼      ▼        ▼      │
#        │ execute execute  execute │
#        │     │      │        │      │
#        │     └──────┴────────┴──────┘
#        │              │
#        │              ▼
#        │     ┌────────────────────┐
#        │     │  supervisor_route  │
#        │     └────────────────────┘
#        │
#        └───────────END─────────────┘
#
# aggregate节点和simple_response节点之后都是END
# ================================================================

# 构建Supervisor工作流图
workflow = StateGraph(SupervisorState)

# 添加supervisor节点
workflow.add_node("intent_classify", _intent_classify_node)
workflow.add_node("simple_response", _simple_response_node)
workflow.add_node("supervisor_plan", _plan_node)
workflow.add_node("supervisor_route", _route_node)
workflow.add_node("execute", _execute_node)
workflow.add_node("aggregate", _aggregate_node)

# 将子agent的graph作为子图添加到supervisor graph中
workflow.add_node("task_agent", task_graph)
workflow.add_node("schedule_agent", schedule_graph)
workflow.add_node("note_agent", note_graph)

# 设置入口点
workflow.set_entry_point("intent_classify")

# 添加条件边：从intent_classify根据判断结果路由
workflow.add_conditional_edges(
    "intent_classify",
    _intent_decision,
    {
        "plan": "supervisor_plan",
        "simple_response": "simple_response"
    }
)

# 添加边
workflow.add_edge("simple_response", END)
workflow.add_edge("supervisor_plan", "supervisor_route")
workflow.add_edge("execute", "supervisor_route")
workflow.add_edge("aggregate", END)

# 添加条件边：从supervisor_route到各个子agent或aggregate
workflow.add_conditional_edges(
    "supervisor_route",
    _route_decision,
    {
        "task_agent": "task_agent",
        "schedule_agent": "schedule_agent",
        "note_agent": "note_agent",
        "aggregate": "aggregate",
        "end": END
    }
)

# 子agent执行后都转到execute节点
workflow.add_edge("task_agent", "execute")
workflow.add_edge("schedule_agent", "execute")
workflow.add_edge("note_agent", "execute")

# 编译graph，传入checkpointer
if _checkpointer:
    graph = workflow.compile(checkpointer=_checkpointer)
else:
    graph = workflow.compile()

# 将checkpointer和store作为graph的属性
graph.checkpointer = _checkpointer
graph.store = _store
