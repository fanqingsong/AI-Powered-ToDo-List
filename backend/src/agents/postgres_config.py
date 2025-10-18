"""
PostgreSQL配置模块
提供PostgreSQL连接和store的配置功能
"""
import os
import uuid
try:
    from langchain_postgres import PostgresChatMessageHistory
except ImportError as e:
    print(f"Warning: Could not import PostgreSQL store: {e}")
    PostgresChatMessageHistory = None


def get_postgres_connection_string():
    """获取PostgreSQL连接字符串"""
    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db = os.getenv("POSTGRES_DB", "ai_todo_db")
    postgres_user = os.getenv("POSTGRES_USER", "ai_todo_user")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "ai_todo_password")
    
    return (
        f"postgresql://{postgres_user}:{postgres_password}"
        f"@{postgres_host}:{postgres_port}/{postgres_db}"
    )


def get_postgres_store():
    """获取PostgreSQL store"""
    if PostgresChatMessageHistory is None:
        print("PostgresChatMessageHistory 不可用")
        return None
    try:
        import psycopg
        # 创建同步连接
        sync_connection = psycopg.connect(get_postgres_connection_string())
        store = PostgresChatMessageHistory(
            "message_store",
            str(uuid.uuid4()),
            sync_connection=sync_connection
        )
        return store
    except Exception as e:
        print(f"创建PostgreSQL store失败: {e}")
        return None
