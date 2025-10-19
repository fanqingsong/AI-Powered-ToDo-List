from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ScheduleBase(BaseModel):
    """日程基础模型"""
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    is_all_day: bool = False
    location: Optional[str] = None
    color: str = "#1890ff"


class ScheduleCreate(ScheduleBase):
    """创建日程模型"""
    pass


class ScheduleUpdate(BaseModel):
    """更新日程模型"""
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_all_day: Optional[bool] = None
    location: Optional[str] = None
    color: Optional[str] = None


class Schedule(ScheduleBase):
    """日程响应模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduleListResponse(BaseModel):
    """日程列表响应模型"""
    schedules: list[Schedule]
    total: int
    page: int
    page_size: int
