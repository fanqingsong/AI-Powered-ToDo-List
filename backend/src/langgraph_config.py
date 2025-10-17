"""
LangGraph PostgreSQL 配置
提供 checkpointer 和 store 的配置
"""
import os
from typing import Optional
try:
    from langgraph.checkpoint.postgres import PostgresSaver
    from langchain_postgres import PostgresChatMessageHistory, PostgresSaver as LangChainPostgresSaver
except ImportError as e:
    print(f"Warning: Could not import PostgreSQL checkpointer: {e}")
    PostgresSaver = None
    PostgresChatMessageHistory = None
    LangChainPostgresSaver = None


class LangGraphPostgresConfig:
    """LangGraph PostgreSQL 配置类"""
    
    def __init__(self):
        self.postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        self.postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.postgres_db = os.getenv("POSTGRES_DB", "ai_todo_db")
        self.postgres_user = os.getenv("POSTGRES_USER", "ai_todo_user")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD", "ai_todo_password")
        
        # 构建连接字符串
        self.connection_string = (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    def get_checkpointer(self):
        """获取PostgreSQL checkpointer"""
        if PostgresSaver is None:
            print("PostgresSaver 不可用")
            return None
        try:
            checkpointer = PostgresSaver.from_conn_string(self.connection_string)
            return checkpointer
        except Exception as e:
            print(f"创建PostgreSQL checkpointer失败: {e}")
            return None
    
    def get_store(self):
        """获取PostgreSQL store"""
        if PostgresChatMessageHistory is None:
            print("PostgresChatMessageHistory 不可用")
            return None
        try:
            store = PostgresChatMessageHistory(
                connection_string=self.connection_string,
                session_id="default_session"
            )
            return store
        except Exception as e:
            print(f"创建PostgreSQL store失败: {e}")
            return None
    
    def get_langchain_postgres_saver(self):
        """获取LangChain PostgreSQL saver"""
        if LangChainPostgresSaver is None:
            print("LangChainPostgresSaver 不可用")
            return None
        try:
            saver = LangChainPostgresSaver.from_conn_string(self.connection_string)
            return saver
        except Exception as e:
            print(f"创建LangChain PostgreSQL saver失败: {e}")
            return None


# 全局配置实例
langgraph_config = LangGraphPostgresConfig()
