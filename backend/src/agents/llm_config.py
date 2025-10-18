"""
LLM配置模块
提供多种LLM提供商的配置和初始化功能
"""
import os
from langchain_openai import ChatOpenAI


def get_llm() -> ChatOpenAI:
    """初始化 LLM
    
    Returns:
        ChatOpenAI: 配置好的LLM实例
    """
    # 支持多种 LLM 提供商
    if os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_ENDPOINT"):
        # Azure OpenAI 配置
        return ChatOpenAI(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"),
            temperature=0.1,
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            base_url=f"{os.getenv('AZURE_OPENAI_ENDPOINT')}openai/deployments/{os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o-mini')}/",
            default_query={"api-version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")}
        )
    elif os.getenv("OPENAI_API_KEY"):
        # 标准 OpenAI API
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    elif os.getenv("ANTHROPIC_API_KEY"):
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-3-sonnet-20240229",
            temperature=0.1,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    else:
        # 使用本地模型或默认配置
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key="dummy-key"  # 将使用模拟响应
        )


def is_llm_available() -> bool:
    """检查 LLM 是否可用
    
    Returns:
        bool: LLM是否可用
    """
    return bool(
        os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_ENDPOINT") or
        os.getenv("OPENAI_API_KEY") or 
        os.getenv("ANTHROPIC_API_KEY")
    )
