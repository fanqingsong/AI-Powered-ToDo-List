"""
Schedule子Agent的Prompt配置
"""

from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta


def _format_tools_list(tool_definitions: List[Dict[str, Any]]) -> str:
    """格式化工具列表为字符串"""
    if not tool_definitions:
        return "- 暂无可用工具"
    
    tool_lines = []
    for tool_def in tool_definitions:
        if tool_def.get("type") == "function" and "function" in tool_def:
            func = tool_def["function"]
            name = func.get("name", "")
            description = func.get("description", "")
            if name:
                tool_lines.append(f"- {name}: {description}")
    
    return "\n".join(tool_lines) if tool_lines else "- 暂无可用工具"


def get_schedule_agent_prompt(tool_definitions: List[Dict[str, Any]] = None) -> str:
    """获取Schedule子Agent的系统提示词
    
    Args:
        tool_definitions: 工具定义列表，用于动态生成工具列表
    """
    # 获取当前日期和时间（使用UTC+8时区，中国时区）
    now = datetime.now(timezone(timedelta(hours=8)))
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    
    base_prompt = """你是一个专门处理日程管理的AI助手。

你的职责：
- 创建、查询、更新、删除日程安排
- 理解用户的日程管理需求
- 使用提供的工具完成日程操作

重要提示 - 日期和时间处理：
- 当前日期和时间：{current_datetime} (UTC+8)
- 当前日期：{current_date}
- 明天日期：{tomorrow}
- 当用户说"明天"时，指的是 {tomorrow}
- 当用户说"今天"时，指的是 {current_date}
- 所有时间必须使用ISO格式（如：2024-01-02T09:00:00+08:00），包含时区信息
- 如果用户没有指定具体时间，默认使用09:00-10:00

可用工具：
{tools_list}

请专注于日程管理，使用合适的工具完成用户请求。在创建日程时，务必使用正确的日期和时间。"""
    
    if tool_definitions:
        tools_list = _format_tools_list(tool_definitions)
    else:
        tools_list = "- 工具列表将在运行时动态加载"
    
    return base_prompt.format(
        tools_list=tools_list,
        current_datetime=current_datetime,
        current_date=current_date,
        tomorrow=tomorrow
    )

