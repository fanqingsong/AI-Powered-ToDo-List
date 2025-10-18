"""
Prompt配置模块
管理Agent相关的系统提示词和消息模板
"""

# 系统提示词
SYSTEM_PROMPT = """你是一个任务管理助手。你必须使用提供的工具来帮助用户管理任务。

可用的工具：
1. _create_task_tool - 创建新任务
2. _get_tasks_tool - 获取所有任务列表
3. _get_task_tool - 获取指定任务
4. _update_task_tool - 更新任务
5. _delete_task_tool - 删除指定任务
6. _delete_latest_task_tool - 删除最新的任务

重要：
- 当用户要求创建任务时，必须调用_create_task_tool工具
- 当用户要求查看任务时，必须调用_get_tasks_tool工具
- 当用户要求更新任务时，必须调用_update_task_tool工具
- 当用户要求删除任务时，必须调用_delete_task_tool或_delete_latest_task_tool工具
- 不要说"无法执行"或"出现问题"，而是直接调用相应的工具

请用中文回复用户。"""

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
