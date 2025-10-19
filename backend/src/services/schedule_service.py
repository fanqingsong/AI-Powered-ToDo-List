from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
from datetime import datetime, date
from ..models.database_models import ScheduleDB
from ..models.schedule import Schedule, ScheduleCreate, ScheduleUpdate, ScheduleListResponse


class ScheduleService:
    """日程管理服务"""
    
    def __init__(self):
        pass

    async def create_schedule(
        self, 
        db: AsyncSession, 
        schedule_data: ScheduleCreate, 
        user_id: int
    ) -> Schedule:
        """创建日程"""
        db_schedule = ScheduleDB(
            title=schedule_data.title,
            description=schedule_data.description,
            start_time=schedule_data.start_time,
            end_time=schedule_data.end_time,
            is_all_day=schedule_data.is_all_day,
            location=schedule_data.location,
            color=schedule_data.color,
            user_id=user_id
        )
        
        db.add(db_schedule)
        await db.commit()
        await db.refresh(db_schedule)
        
        return Schedule.model_validate(db_schedule)

    async def get_schedule(
        self, 
        db: AsyncSession, 
        schedule_id: int, 
        user_id: int
    ) -> Optional[Schedule]:
        """获取单个日程"""
        result = await db.execute(
            select(ScheduleDB)
            .where(and_(ScheduleDB.id == schedule_id, ScheduleDB.user_id == user_id))
        )
        db_schedule = result.scalar_one_or_none()
        
        if db_schedule:
            return Schedule.model_validate(db_schedule)
        return None

    async def get_schedules(
        self,
        db: AsyncSession,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50
    ) -> ScheduleListResponse:
        """获取日程列表"""
        query = select(ScheduleDB).where(ScheduleDB.user_id == user_id)
        
        # 添加时间过滤
        if start_date:
            query = query.where(ScheduleDB.start_time >= start_date)
        if end_date:
            query = query.where(ScheduleDB.end_time <= end_date)
        
        # 按开始时间排序
        query = query.order_by(ScheduleDB.start_time)
        
        # 分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        schedules = result.scalars().all()
        
        # 获取总数
        count_query = select(func.count(ScheduleDB.id)).where(ScheduleDB.user_id == user_id)
        if start_date:
            count_query = count_query.where(ScheduleDB.start_time >= start_date)
        if end_date:
            count_query = count_query.where(ScheduleDB.end_time <= end_date)
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        return ScheduleListResponse(
            schedules=[Schedule.model_validate(schedule) for schedule in schedules],
            total=total,
            page=page,
            page_size=page_size
        )

    async def get_schedules_by_date_range(
        self,
        db: AsyncSession,
        user_id: int,
        start_date: date,
        end_date: date
    ) -> List[Schedule]:
        """获取指定日期范围内的日程"""
        # 将日期转换为datetime，开始日期为00:00:00，结束日期为23:59:59
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        result = await db.execute(
            select(ScheduleDB)
            .where(
                and_(
                    ScheduleDB.user_id == user_id,
                    ScheduleDB.start_time >= start_datetime,
                    ScheduleDB.end_time <= end_datetime
                )
            )
            .order_by(ScheduleDB.start_time)
        )
        
        schedules = result.scalars().all()
        return [Schedule.model_validate(schedule) for schedule in schedules]

    async def update_schedule(
        self,
        db: AsyncSession,
        schedule_id: int,
        user_id: int,
        schedule_data: ScheduleUpdate
    ) -> Optional[Schedule]:
        """更新日程"""
        result = await db.execute(
            select(ScheduleDB)
            .where(and_(ScheduleDB.id == schedule_id, ScheduleDB.user_id == user_id))
        )
        db_schedule = result.scalar_one_or_none()
        
        if not db_schedule:
            return None
        
        # 更新字段
        update_data = schedule_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_schedule, field, value)
        
        await db.commit()
        await db.refresh(db_schedule)
        
        return Schedule.model_validate(db_schedule)

    async def delete_schedule(
        self,
        db: AsyncSession,
        schedule_id: int,
        user_id: int
    ) -> bool:
        """删除日程"""
        result = await db.execute(
            select(ScheduleDB)
            .where(and_(ScheduleDB.id == schedule_id, ScheduleDB.user_id == user_id))
        )
        db_schedule = result.scalar_one_or_none()
        
        if not db_schedule:
            return False
        
        await db.delete(db_schedule)
        await db.commit()
        
        return True

    async def get_upcoming_schedules(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 10
    ) -> List[Schedule]:
        """获取即将到来的日程"""
        now = datetime.now()
        
        result = await db.execute(
            select(ScheduleDB)
            .where(
                and_(
                    ScheduleDB.user_id == user_id,
                    ScheduleDB.start_time >= now
                )
            )
            .order_by(ScheduleDB.start_time)
            .limit(limit)
        )
        
        schedules = result.scalars().all()
        return [Schedule.model_validate(schedule) for schedule in schedules]
