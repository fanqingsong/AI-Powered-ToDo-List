import asyncio
from typing import List, Optional
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload

from ..database import get_db_session, AsyncSessionLocal
from ..models import TaskItem
from ..models.database_models import TaskDB


class TaskService:
    """
    Service class for managing tasks with CRUD operations using PostgreSQL.
    This service provides all the necessary operations for task management.
    """
    
    def __init__(self):
        pass
    
    async def get_all_tasks(self, user_id: Optional[int] = None) -> List[TaskItem]:
        """Get all tasks from the database."""
        async with get_db_session() as session:
            query = select(TaskDB)
            if user_id is not None:
                query = query.where(TaskDB.user_id == user_id)
            query = query.order_by(TaskDB.id)
            
            result = await session.execute(query)
            tasks_db = result.scalars().all()
            
            return [
                TaskItem(
                    id=task.id,
                    title=task.title,
                    isComplete=task.is_complete
                )
                for task in tasks_db
            ]
    
    async def get_task_by_id(self, task_id: int, user_id: Optional[int] = None) -> Optional[TaskItem]:
        """Get a task by its ID."""
        async with get_db_session() as session:
            query = select(TaskDB).where(TaskDB.id == task_id)
            if user_id is not None:
                query = query.where(TaskDB.user_id == user_id)
            
            result = await session.execute(query)
            task_db = result.scalar_one_or_none()
            
            if task_db:
                return TaskItem(
                    id=task_db.id,
                    title=task_db.title,
                    isComplete=task_db.is_complete
                )
            return None
    
    async def add_task(self, title: str, is_complete: bool = False, user_id: Optional[int] = None) -> TaskItem:
        """Add a new task to the database."""
        async with get_db_session() as session:
            task_db = TaskDB(
                title=title,
                is_complete=is_complete,
                user_id=user_id
            )
            session.add(task_db)
            await session.flush()  # 获取ID但不提交
            
            return TaskItem(
                id=task_db.id,
                title=task_db.title,
                isComplete=task_db.is_complete
            )
    
    async def update_task(self, task_id: int, title: Optional[str] = None, is_complete: Optional[bool] = None, user_id: Optional[int] = None) -> bool:
        """Update a task by its ID."""
        async with get_db_session() as session:
            # 首先获取当前任务
            query = select(TaskDB).where(TaskDB.id == task_id)
            if user_id is not None:
                query = query.where(TaskDB.user_id == user_id)
            
            result = await session.execute(query)
            task_db = result.scalar_one_or_none()
            
            if not task_db:
                return False
            
            # 更新字段
            if title is not None:
                task_db.title = title
            if is_complete is not None:
                task_db.is_complete = is_complete
            
            await session.flush()
            return True
    
    async def delete_task(self, task_id: int, user_id: Optional[int] = None) -> bool:
        """Delete a task by its ID."""
        async with get_db_session() as session:
            query = delete(TaskDB).where(TaskDB.id == task_id)
            if user_id is not None:
                query = query.where(TaskDB.user_id == user_id)
            
            result = await session.execute(query)
            return result.rowcount > 0
    
    async def get_task_count(self, user_id: Optional[int] = None) -> int:
        """Get the total number of tasks."""
        async with get_db_session() as session:
            query = select(func.count(TaskDB.id))
            if user_id is not None:
                query = query.where(TaskDB.user_id == user_id)
            
            result = await session.execute(query)
            return result.scalar()
    
    async def get_completed_task_count(self, user_id: Optional[int] = None) -> int:
        """Get the number of completed tasks."""
        async with get_db_session() as session:
            query = select(func.count(TaskDB.id)).where(TaskDB.is_complete == True)
            if user_id is not None:
                query = query.where(TaskDB.user_id == user_id)
            
            result = await session.execute(query)
            return result.scalar()
    
    async def migrate_from_sqlite(self, sqlite_db_path: str = "tasks.db") -> int:
        """Migrate tasks from SQLite to PostgreSQL."""
        import sqlite3
        
        migrated_count = 0
        
        try:
            # 连接SQLite数据库
            conn = sqlite3.connect(sqlite_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks ORDER BY id")
            rows = cursor.fetchall()
            conn.close()
            
            # 迁移到PostgreSQL
            async with get_db_session() as session:
                for row in rows:
                    task_id, title, is_complete = row
                    
                    # 检查是否已存在
                    existing_task = await session.execute(
                        select(TaskDB).where(TaskDB.id == task_id)
                    )
                    if existing_task.scalar_one_or_none():
                        continue  # 跳过已存在的任务
                    
                    # 创建新任务
                    task_db = TaskDB(
                        id=task_id,  # 保持原有ID
                        title=title,
                        is_complete=bool(is_complete),
                        user_id=None  # SQLite中没有用户关联
                    )
                    session.add(task_db)
                    migrated_count += 1
                
                await session.flush()
            
            print(f"成功迁移 {migrated_count} 个任务从SQLite到PostgreSQL")
            return migrated_count
            
        except Exception as e:
            print(f"迁移任务时出错: {e}")
            return migrated_count