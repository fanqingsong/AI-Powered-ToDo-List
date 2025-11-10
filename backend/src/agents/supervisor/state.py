"""
Supervisor Agent 状态定义
扩展基础AgentState，支持plan-execute模式
"""

from typing import Annotated, List, Dict, Any, Optional, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """基础Agent状态定义"""
    messages: Annotated[list, add_messages]


def merge_execution_results(x: List, y: List) -> List:
    """合并执行结果列表"""
    if isinstance(x, list) and isinstance(y, list):
        return x + y
    return (x or []) + (y or [])


class ExecutionStep(TypedDict):
    """执行步骤定义"""
    agent: Literal["task", "schedule", "note"]  # 子agent类型
    action: str  # 操作类型（create, update, delete, query等）
    params: Dict[str, Any]  # 操作参数
    description: str  # 步骤描述


class ExecutionPlan(TypedDict):
    """执行计划定义"""
    steps: List[ExecutionStep]  # 执行步骤列表
    summary: str  # 计划摘要


class ExecutionResult(TypedDict):
    """执行结果定义"""
    step_index: int  # 步骤索引
    agent: str  # 执行的子agent
    success: bool  # 是否成功
    result: Any  # 执行结果
    error: Optional[str]  # 错误信息（如果有）


class SupervisorState(AgentState):
    """Supervisor Agent状态
    
    扩展基础AgentState，添加plan-execute模式所需的状态字段
    """
    # 用户相关
    user_id: Optional[int]  # 当前用户ID
    
    # 执行计划相关
    plan: Optional[ExecutionPlan]  # 当前执行计划
    current_step: int  # 当前执行步骤索引（从0开始）
    
    # 执行结果相关
    execution_results: Annotated[List[ExecutionResult], merge_execution_results]  # 所有步骤的执行结果
    
    # 路由相关
    selected_agent: Optional[Literal["task", "schedule", "note"]]  # 当前选中的子agent类型
    
    # 上下文相关
    agent_context: Dict[str, Any]  # 传递给子agent的上下文信息
    
    # 控制流相关
    should_continue: bool  # 是否继续执行下一步
    is_planning: bool  # 是否处于规划阶段
    is_executing: bool  # 是否处于执行阶段
    is_aggregating: bool  # 是否处于汇总阶段
    
    # 意图分类相关
    needs_business_data: Optional[bool]  # 是否需要调用业务数据（任务、日程、笔记）

