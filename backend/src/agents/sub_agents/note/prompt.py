"""
Note子Agent的Prompt配置
"""

from typing import List, Dict, Any


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


def get_note_agent_prompt(tool_definitions: List[Dict[str, Any]] = None) -> str:
    """获取Note子Agent的系统提示词
    
    Args:
        tool_definitions: 工具定义列表，用于动态生成工具列表
    """
    base_prompt = """你是一个专门处理笔记管理的AI助手。

你的职责：
- 创建、查询、更新、删除笔记
- 搜索和管理笔记内容
- 理解用户的笔记管理需求
- 使用提供的工具完成笔记操作

可用工具：
{tools_list}

请专注于笔记管理，使用合适的工具完成用户请求。"""
    
    if tool_definitions:
        tools_list = _format_tools_list(tool_definitions)
    else:
        tools_list = "- 工具列表将在运行时动态加载"
    
    return base_prompt.format(tools_list=tools_list)

