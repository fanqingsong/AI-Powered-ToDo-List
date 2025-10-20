import asyncio
from typing import List, Optional
from sqlalchemy import select, update, delete, func, create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from ..models import TaskItem
from ..models.database_models import TaskDB
import os


class SyncTaskService:
    """
    同步版本的TaskService，用于在工具中调用
    避免异步事件循环问题
    """
    
    def __init__(self):
        # 创建同步数据库连接
        POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
        POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
        POSTGRES_DB = os.getenv("POSTGRES_DB", "ai_todo_db")
        POSTGRES_USER = os.getenv("POSTGRES_USER", "ai_todo_user")
        POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ai_todo_password")
        
        # 构建同步数据库URL
        SYNC_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        
        # 创建同步引擎
        self.engine = create_engine(
            SYNC_DATABASE_URL,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        # 创建会话工厂
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()
    
    def get_all_tasks(self, user_id: Optional[int] = None) -> List[TaskItem]:
        """获取所有任务"""
        with self.get_session() as session:
            query = select(TaskDB)
            if user_id is not None:
                query = query.where(TaskDB.user_id == user_id)
            query = query.order_by(TaskDB.id)
            
            result = session.execute(query)
            tasks_db = result.scalars().all()
            
            return [
                TaskItem(
                    id=task.id,
                    title=task.title,
                    isComplete=task.is_complete
                )
                for task in tasks_db
            ]
    
    def get_task_by_id(self, task_id: int, user_id: Optional[int] = None) -> Optional[TaskItem]:
        """根据ID获取任务"""
        with self.get_session() as session:
            query = select(TaskDB).where(TaskDB.id == task_id)
            if user_id is not None:
                query = query.where(TaskDB.user_id == user_id)
            
            result = session.execute(query)
            task_db = result.scalar_one_or_none()
            
            if task_db:
                return TaskItem(
                    id=task_db.id,
                    title=task_db.title,
                    isComplete=task_db.is_complete
                )
            return None
    
    def add_task(self, title: str, is_complete: bool = False, user_id: Optional[int] = None) -> TaskItem:
        """添加新任务"""
        with self.get_session() as session:
            task_db = TaskDB(
                title=title,
                is_complete=is_complete,
                user_id=user_id
            )
            session.add(task_db)
            session.flush()  # 获取ID
            session.commit()  # 提交事务，确保数据持久化
            
            return TaskItem(
                id=task_db.id,
                title=task_db.title,
                isComplete=task_db.is_complete
            )
    
    def update_task(self, task_id: int, title: Optional[str] = None, is_complete: Optional[bool] = None, user_id: Optional[int] = None) -> Optional[TaskItem]:
        """更新任务"""
        with self.get_session() as session:
            # 首先获取当前任务
            query = select(TaskDB).where(TaskDB.id == task_id)
            if user_id is not None:
                query = query.where(TaskDB.user_id == user_id)
            
            result = session.execute(query)
            task_db = result.scalar_one_or_none()
            
            if not task_db:
                return None
            
            # 更新字段
            if title is not None:
                task_db.title = title
            if is_complete is not None:
                task_db.is_complete = is_complete
            
            session.flush()
            session.commit()  # 提交事务，确保数据持久化
            
            return TaskItem(
                id=task_db.id,
                title=task_db.title,
                isComplete=task_db.is_complete
            )
    
    def get_task_by_title(self, title: str, user_id: Optional[int] = None) -> Optional[TaskItem]:
        """根据标题模糊匹配获取任务（如果有多个匹配任务，返回第一个）"""
        with self.get_session() as session:
            # 使用LIKE进行模糊匹配，支持部分匹配
            query = select(TaskDB).where(TaskDB.title.like(f"%{title}%"))
            if user_id is not None:
                query = query.where(TaskDB.user_id == user_id)
            query = query.order_by(TaskDB.id).limit(1)  # 只获取第一个
            
            result = session.execute(query)
            task_db = result.scalar_one_or_none()
            
            if task_db:
                return TaskItem(
                    id=task_db.id,
                    title=task_db.title,
                    isComplete=task_db.is_complete
                )
            return None
    
    def delete_task(self, task_id: int, user_id: Optional[int] = None) -> bool:
        """删除任务"""
        with self.get_session() as session:
            query = delete(TaskDB).where(TaskDB.id == task_id)
            if user_id is not None:
                query = query.where(TaskDB.user_id == user_id)
            
            result = session.execute(query)
            session.commit()  # 提交事务，确保数据持久化
            return result.rowcount > 0
    
    def delete_task_by_title(self, title: str, user_id: Optional[int] = None) -> bool:
        """根据标题模糊匹配删除任务"""
        with self.get_session() as session:
            # 使用LIKE进行模糊匹配，支持部分匹配
            query = delete(TaskDB).where(TaskDB.title.like(f"%{title}%"))
            if user_id is not None:
                query = query.where(TaskDB.user_id == user_id)
            
            result = session.execute(query)
            session.commit()  # 提交事务，确保数据持久化
            return result.rowcount > 0
