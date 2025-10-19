from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, date
from ..database import get_db
from ..services.schedule_service import ScheduleService
from ..models.schedule import Schedule, ScheduleCreate, ScheduleUpdate, ScheduleListResponse
from ..models.auth import User
from ..auth.dependencies import get_current_user

router = APIRouter()
schedule_service = ScheduleService()


@router.post("/", response_model=Schedule)
async def create_schedule(
    schedule_data: ScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建日程"""
    try:
        schedule = await schedule_service.create_schedule(
            db=db,
            schedule_data=schedule_data,
            user_id=current_user.id
        )
        return schedule
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建日程失败: {str(e)}")


@router.get("/", response_model=ScheduleListResponse)
async def get_schedules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=100, description="每页数量")
):
    """获取日程列表"""
    try:
        schedules = await schedule_service.get_schedules(
            db=db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size
        )
        return schedules
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取日程列表失败: {str(e)}")


@router.get("/range", response_model=list[Schedule])
async def get_schedules_by_date_range(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期")
):
    """获取指定日期范围内的日程"""
    try:
        schedules = await schedule_service.get_schedules_by_date_range(
            db=db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        return schedules
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取日程失败: {str(e)}")


@router.get("/upcoming", response_model=list[Schedule])
async def get_upcoming_schedules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=50, description="数量限制")
):
    """获取即将到来的日程"""
    try:
        schedules = await schedule_service.get_upcoming_schedules(
            db=db,
            user_id=current_user.id,
            limit=limit
        )
        return schedules
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取即将到来的日程失败: {str(e)}")


@router.get("/{schedule_id}", response_model=Schedule)
async def get_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取单个日程"""
    schedule = await schedule_service.get_schedule(
        db=db,
        schedule_id=schedule_id,
        user_id=current_user.id
    )
    
    if not schedule:
        raise HTTPException(status_code=404, detail="日程不存在")
    
    return schedule


@router.put("/{schedule_id}", response_model=Schedule)
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新日程"""
    schedule = await schedule_service.update_schedule(
        db=db,
        schedule_id=schedule_id,
        user_id=current_user.id,
        schedule_data=schedule_data
    )
    
    if not schedule:
        raise HTTPException(status_code=404, detail="日程不存在")
    
    return schedule


@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除日程"""
    success = await schedule_service.delete_schedule(
        db=db,
        schedule_id=schedule_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="日程不存在")
    
    return {"message": "日程删除成功"}


def create_schedule_routes():
    """创建日程路由"""
    return router
