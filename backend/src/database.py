import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData
from contextlib import asynccontextmanager

# 数据库配置
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ai_todo_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "ai_todo_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ai_todo_password")

# 构建数据库URL
DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # 设置为True可以看到SQL语句
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 创建会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 创建基础模型类
Base = declarative_base()

# 元数据
metadata = MetaData()


@asynccontextmanager
async def get_db_session():
    """获取数据库会话的上下文管理器"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database():
    """初始化数据库连接"""
    try:
        async with engine.begin() as conn:
            # 导入所有模型以确保表被创建
            from .models.database_models import (
                TaskDB, ShortTermMemoryDB, LongTermMemoryDB, 
                TaskContextMemoryDB, ConversationHistoryDB, 
                UserDB, UserSessionDB
            )
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
        print("数据库连接初始化成功，所有表已创建")
    except Exception as e:
        print(f"数据库连接初始化失败: {e}")
        raise


async def close_database():
    """关闭数据库连接"""
    await engine.dispose()
    print("数据库连接已关闭")
