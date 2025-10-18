"""
使用官方 PostgresSaver 的简化 checkpointer 模块
"""
from langgraph.checkpoint.postgres import PostgresSaver


def get_postgres_checkpointer(connection_string: str) -> PostgresSaver:
    """获取官方的 PostgreSQL checkpointer"""
    checkpointer = PostgresSaver.from_conn_string(connection_string)
    # 设置数据库表
    checkpointer.setup()
    return checkpointer
