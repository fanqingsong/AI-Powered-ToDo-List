"""
Prompt配置模块
管理Agent相关的系统提示词和消息模板
"""

from typing import List, Dict, Any, Optional

# 基础系统提示词模板
BASE_SYSTEM_PROMPT_TEMPLATE = """你是一个智能的AI助手，专门帮助用户管理任务和提供个性化服务。

## 你的身份和能力：
- 你是用户的专属AI助手，能够识别和记住用户身份
- 你可以帮助用户管理任务、回答问题、提供建议
- 你具有记忆能力，能够记住用户的偏好和历史对话
- 你能够访问用户的登录信息，提供精准的个性化服务

## 可用的工具：
{tools_description}

## 重要指导原则：
- 当用户询问"我是谁"或身份相关问题时，你应该：
  * 直接使用提供的用户信息回答
  * 展现你对用户身份的准确了解
  * 提供个性化的回答，体现专属服务
- 不要说"无法执行"或"出现问题"，而是直接调用相应的工具
- 始终保持友好、专业的语调
- 展现你的智能和个性化服务能力
- 基于用户信息提供精准的服务和建议

请用中文回复用户，并展现你的智能和个性化服务能力。"""



def generate_dynamic_system_prompt(
    task_tools: Optional[Any] = None,
    frontend_tools_config: Optional[List[Dict[str, Any]]] = None
) -> str:
    """动态生成系统提示词
    
    Args:
        task_tools: 任务工具实例，用于获取工具定义
        frontend_tools_config: 前端工具配置列表
        
    Returns:
        动态生成的系统提示词
    """
    tools_description = ""
    
    if task_tools:
        # 获取工具定义
        tool_definitions = task_tools.get_tool_definitions()
        
        # 构建工具描述
        tool_descriptions = []
        for i, tool_def in enumerate(tool_definitions, 1):
            tool_name = tool_def["function"]["name"]
            tool_desc = tool_def["function"]["description"]
            
            # 格式化工具描述
            if tool_name.startswith("_"):
                # 移除下划线前缀
                display_name = tool_name[1:]
            else:
                display_name = tool_name
                
            tool_descriptions.append(f"{i}. {display_name} - {tool_desc}")
        
        tools_description = "\n".join(tool_descriptions)
    
    # 如果有前端工具配置，添加前端工具描述
    if frontend_tools_config:
        frontend_tools_desc = []
        start_index = len(tool_definitions) + 1 if task_tools else 10
        
        for i, tool_config in enumerate(frontend_tools_config, start_index):
            tool_name = tool_config.get("name", f"frontend_tool_{i}")
            tool_desc = tool_config.get("description", "前端工具")
            frontend_tools_desc.append(f"{i}. {tool_name} - {tool_desc}")
        
        if frontend_tools_desc:
            tools_description += "\n" + "\n".join(frontend_tools_desc)
    
    return BASE_SYSTEM_PROMPT_TEMPLATE.format(tools_description=tools_description)

# 错误消息模板
ERROR_MESSAGES = {
    "llm_unavailable": """抱歉，AI 功能当前不可用。请配置以下任一环境变量以启用 AI 功能：

• Azure OpenAI: AZURE_OPENAI_API_KEY 和 AZURE_OPENAI_ENDPOINT
• 标准 OpenAI: OPENAI_API_KEY
• Anthropic: ANTHROPIC_API_KEY

您仍然可以使用以下功能：
- 查看任务列表
- 创建新任务
- 更新任务状态
- 删除任务""",
    
    "connection_error": """抱歉，AI 功能当前不可用。请配置以下任一环境变量以启用 AI 功能：

• Azure OpenAI: AZURE_OPENAI_API_KEY 和 AZURE_OPENAI_ENDPOINT
• 标准 OpenAI: OPENAI_API_KEY
• Anthropic: ANTHROPIC_API_KEY

您仍然可以使用以下功能：
- 查看任务列表
- 创建新任务
- 更新任务状态
- 删除任务""",
    
    "general_error": "抱歉，处理您的消息时出现了错误：{error_msg}"
}

# 成功消息模板
SUCCESS_MESSAGES = {
    "conversation_saved": "对话已保存到短期记忆: session_id={session_id}",
    "checkpointer_initialized": "内置PostgreSQL checkpointer 初始化成功",
    "store_initialized": "PostgreSQL store 初始化成功"
}

# 调试消息模板
DEBUG_MESSAGES = {
    "conversation_save_failed": "保存对话到短期记忆失败: {error}",
    "checkpointer_init_failed": "内置PostgreSQL checkpointer 初始化失败: {error}",
    "store_init_failed": "PostgreSQL store 初始化失败，将使用内存模式",
    "store_init_error": "初始化 store 失败: {error}"
}
