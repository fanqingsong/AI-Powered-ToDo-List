"""
Prompt配置模块
管理Agent相关的消息模板
"""

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
