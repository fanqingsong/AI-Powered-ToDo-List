from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from ..services.analytics_service import AnalyticsService
from ..models.analytics import AnalyticsRequest, AnalyticsResponse, TimeRange
from ..auth.dependencies import get_current_user
from ..models.auth import User

router = APIRouter()

# 创建分析服务实例
analytics_service = AnalyticsService()


@router.get("/overview", response_model=AnalyticsResponse)
async def get_analytics_overview(
    time_range: TimeRange = Query(TimeRange.MONTH, description="时间范围"),
    include_charts: bool = Query(True, description="是否包含图表数据"),
    current_user: User = Depends(get_current_user)
):
    """
    获取分析概览数据
    
    - **time_range**: 时间范围 (today, week, month, quarter, year, all)
    - **include_charts**: 是否包含图表数据
    """
    try:
        request = AnalyticsRequest(
            time_range=time_range,
            user_id=current_user.id,
            include_charts=include_charts
        )
        
        analytics_data = await analytics_service.get_analytics_overview(request)
        
        return AnalyticsResponse(
            success=True,
            message="分析数据获取成功",
            data=analytics_data
        )
    
    except Exception as e:
        return AnalyticsResponse(
            success=False,
            message="获取分析数据失败",
            error=str(e)
        )


@router.get("/tasks", response_model=AnalyticsResponse)
async def get_task_analytics(
    time_range: TimeRange = Query(TimeRange.MONTH, description="时间范围"),
    current_user: User = Depends(get_current_user)
):
    """
    获取任务分析数据
    """
    try:
        request = AnalyticsRequest(
            time_range=time_range,
            user_id=current_user.id,
            include_charts=False
        )
        
        analytics_data = await analytics_service.get_analytics_overview(request)
        
        return AnalyticsResponse(
            success=True,
            message="任务分析数据获取成功",
            data=analytics_data
        )
    
    except Exception as e:
        return AnalyticsResponse(
            success=False,
            message="获取任务分析数据失败",
            error=str(e)
        )


@router.get("/notes", response_model=AnalyticsResponse)
async def get_note_analytics(
    time_range: TimeRange = Query(TimeRange.MONTH, description="时间范围"),
    current_user: User = Depends(get_current_user)
):
    """
    获取笔记分析数据
    """
    try:
        request = AnalyticsRequest(
            time_range=time_range,
            user_id=current_user.id,
            include_charts=False
        )
        
        analytics_data = await analytics_service.get_analytics_overview(request)
        
        return AnalyticsResponse(
            success=True,
            message="笔记分析数据获取成功",
            data=analytics_data
        )
    
    except Exception as e:
        return AnalyticsResponse(
            success=False,
            message="获取笔记分析数据失败",
            error=str(e)
        )


@router.get("/schedules", response_model=AnalyticsResponse)
async def get_schedule_analytics(
    time_range: TimeRange = Query(TimeRange.MONTH, description="时间范围"),
    current_user: User = Depends(get_current_user)
):
    """
    获取日程分析数据
    """
    try:
        request = AnalyticsRequest(
            time_range=time_range,
            user_id=current_user.id,
            include_charts=False
        )
        
        analytics_data = await analytics_service.get_analytics_overview(request)
        
        return AnalyticsResponse(
            success=True,
            message="日程分析数据获取成功",
            data=analytics_data
        )
    
    except Exception as e:
        return AnalyticsResponse(
            success=False,
            message="获取日程分析数据失败",
            error=str(e)
        )


@router.get("/productivity", response_model=AnalyticsResponse)
async def get_productivity_metrics(
    current_user: User = Depends(get_current_user)
):
    """
    获取生产力指标
    """
    try:
        request = AnalyticsRequest(
            time_range=TimeRange.TODAY,
            user_id=current_user.id,
            include_charts=False
        )
        
        analytics_data = await analytics_service.get_analytics_overview(request)
        
        return AnalyticsResponse(
            success=True,
            message="生产力指标获取成功",
            data=analytics_data
        )
    
    except Exception as e:
        return AnalyticsResponse(
            success=False,
            message="获取生产力指标失败",
            error=str(e)
        )


@router.get("/charts", response_model=AnalyticsResponse)
async def get_chart_data(
    time_range: TimeRange = Query(TimeRange.MONTH, description="时间范围"),
    chart_type: Optional[str] = Query(None, description="图表类型"),
    current_user: User = Depends(get_current_user)
):
    """
    获取图表数据
    """
    try:
        request = AnalyticsRequest(
            time_range=time_range,
            user_id=current_user.id,
            include_charts=True
        )
        
        analytics_data = await analytics_service.get_analytics_overview(request)
        
        # 如果指定了图表类型，过滤图表数据
        if chart_type:
            filtered_charts = [
                chart for chart in analytics_data.charts 
                if chart.type.value == chart_type
            ]
            analytics_data.charts = filtered_charts
        
        return AnalyticsResponse(
            success=True,
            message="图表数据获取成功",
            data=analytics_data
        )
    
    except Exception as e:
        return AnalyticsResponse(
            success=False,
            message="获取图表数据失败",
            error=str(e)
        )


def create_analytics_routes():
    """创建分析路由"""
    return router
