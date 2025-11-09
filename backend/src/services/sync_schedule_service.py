"""
同步版本的ScheduleService，用于在工具中调用
避免异步事件循环问题
"""

from typing import List, Optional
from sqlalchemy import select, delete, and_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from datetime import datetime, date

from ..models.schedule import Schedule, ScheduleCreate, ScheduleUpdate
from ..models.database_models import ScheduleDB
import os


class SyncScheduleService:
    """
    同步版本的ScheduleService，用于在工具中调用
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
    
    def get_all_schedules(self, user_id: Optional[int] = None) -> List[Schedule]:
        """获取所有日程"""
        with self.get_session() as session:
            query = select(ScheduleDB)
            if user_id is not None:
                query = query.where(ScheduleDB.user_id == user_id)
            query = query.order_by(ScheduleDB.start_time)
            
            result = session.execute(query)
            schedules_db = result.scalars().all()
            
            return [Schedule.model_validate(schedule) for schedule in schedules_db]
    
    def get_schedule_by_id(self, schedule_id: int, user_id: Optional[int] = None) -> Optional[Schedule]:
        """根据ID获取日程"""
        with self.get_session() as session:
            query = select(ScheduleDB).where(ScheduleDB.id == schedule_id)
            if user_id is not None:
                query = query.where(ScheduleDB.user_id == user_id)
            
            result = session.execute(query)
            schedule_db = result.scalar_one_or_none()
            
            if schedule_db:
                return Schedule.model_validate(schedule_db)
            return None
    
    def create_schedule(self, schedule_data: ScheduleCreate, user_id: Optional[int] = None) -> Schedule:
        """创建新日程"""
        with self.get_session() as session:
            schedule_db = ScheduleDB(
                title=schedule_data.title,
                description=schedule_data.description,
                start_time=schedule_data.start_time,
                end_time=schedule_data.end_time,
                is_all_day=schedule_data.is_all_day,
                location=schedule_data.location,
                color=schedule_data.color,
                user_id=user_id
            )
            session.add(schedule_db)
            session.flush()
            session.commit()
            session.refresh(schedule_db)
            
            return Schedule.model_validate(schedule_db)
    
    def update_schedule(self, schedule_id: int, schedule_data: ScheduleUpdate, user_id: Optional[int] = None) -> Optional[Schedule]:
        """更新日程"""
        with self.get_session() as session:
            query = select(ScheduleDB).where(ScheduleDB.id == schedule_id)
            if user_id is not None:
                query = query.where(ScheduleDB.user_id == user_id)
            
            result = session.execute(query)
            schedule_db = result.scalar_one_or_none()
            
            if not schedule_db:
                return None
            
            # 更新字段
            update_data = schedule_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(schedule_db, field, value)
            
            session.flush()
            session.commit()
            session.refresh(schedule_db)
            
            return Schedule.model_validate(schedule_db)
    
    def delete_schedule(self, schedule_id: int, user_id: Optional[int] = None) -> bool:
        """删除日程"""
        with self.get_session() as session:
            query = delete(ScheduleDB).where(ScheduleDB.id == schedule_id)
            if user_id is not None:
                query = query.where(ScheduleDB.user_id == user_id)
            
            result = session.execute(query)
            session.commit()
            return result.rowcount > 0
    
    def get_schedules_by_date_range(
        self, 
        start_date: date, 
        end_date: date, 
        user_id: Optional[int] = None
    ) -> List[Schedule]:
        """获取指定日期范围内的日程"""
        with self.get_session() as session:
            # 将日期转换为datetime
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            query = select(ScheduleDB).where(
                and_(
                    ScheduleDB.start_time >= start_datetime,
                    ScheduleDB.end_time <= end_datetime
                )
            )
            if user_id is not None:
                query = query.where(ScheduleDB.user_id == user_id)
            query = query.order_by(ScheduleDB.start_time)
            
            result = session.execute(query)
            schedules_db = result.scalars().all()
            
            return [Schedule.model_validate(schedule) for schedule in schedules_db]
    
    def get_upcoming_schedules(self, limit: int = 10, user_id: Optional[int] = None) -> List[Schedule]:
        """获取即将到来的日程"""
        with self.get_session() as session:
            now = datetime.now()
            
            query = select(ScheduleDB).where(
                ScheduleDB.start_time >= now
            )
            if user_id is not None:
                query = query.where(ScheduleDB.user_id == user_id)
            query = query.order_by(ScheduleDB.start_time).limit(limit)
            
            result = session.execute(query)
            schedules_db = result.scalars().all()
            
            return [Schedule.model_validate(schedule) for schedule in schedules_db]

