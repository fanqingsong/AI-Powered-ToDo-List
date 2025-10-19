from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class TimeRange(str, Enum):
    """时间范围枚举"""
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    ALL = "all"


class ChartType(str, Enum):
    """图表类型枚举"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"


class TaskAnalytics(BaseModel):
    """任务分析数据模型"""
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    completion_rate: float
    tasks_by_day: List[Dict[str, Any]]
    tasks_by_week: List[Dict[str, Any]]
    tasks_by_month: List[Dict[str, Any]]
    average_completion_time: Optional[float] = None  # 平均完成时间（小时）


class NoteAnalytics(BaseModel):
    """笔记分析数据模型"""
    total_notes: int
    total_words: int
    average_words_per_note: float
    notes_by_category: List[Dict[str, Any]]
    notes_by_day: List[Dict[str, Any]]
    notes_by_week: List[Dict[str, Any]]
    notes_by_month: List[Dict[str, Any]]
    pinned_notes: int
    archived_notes: int
    most_used_tags: List[Dict[str, Any]]


class ScheduleAnalytics(BaseModel):
    """日程分析数据模型"""
    total_schedules: int
    completed_schedules: int
    pending_schedules: int
    completion_rate: float
    schedules_by_day: List[Dict[str, Any]]
    schedules_by_week: List[Dict[str, Any]]
    schedules_by_month: List[Dict[str, Any]]
    schedules_by_priority: List[Dict[str, Any]]
    average_duration: Optional[float] = None  # 平均持续时间（小时）


class UserActivityAnalytics(BaseModel):
    """用户活动分析数据模型"""
    total_users: int
    active_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    user_activity_by_day: List[Dict[str, Any]]
    user_activity_by_week: List[Dict[str, Any]]
    user_activity_by_month: List[Dict[str, Any]]


class ProductivityMetrics(BaseModel):
    """生产力指标数据模型"""
    tasks_completed_today: int
    notes_created_today: int
    schedules_completed_today: int
    total_work_time_today: float  # 总工作时间（小时）
    productivity_score: float  # 生产力评分 (0-100)
    streak_days: int  # 连续活跃天数
    weekly_goal_progress: float  # 周目标完成进度 (0-100)


class ChartData(BaseModel):
    """图表数据模型"""
    title: str
    type: ChartType
    data: List[Dict[str, Any]]
    x_axis: str
    y_axis: str
    colors: Optional[List[str]] = None


class AnalyticsOverview(BaseModel):
    """分析概览数据模型"""
    time_range: TimeRange
    generated_at: datetime
    task_analytics: TaskAnalytics
    note_analytics: NoteAnalytics
    schedule_analytics: ScheduleAnalytics
    user_activity: UserActivityAnalytics
    productivity_metrics: ProductivityMetrics
    charts: List[ChartData]


class AnalyticsRequest(BaseModel):
    """分析请求数据模型"""
    time_range: TimeRange = TimeRange.MONTH
    user_id: Optional[int] = None
    include_charts: bool = True
    chart_types: Optional[List[ChartType]] = None


class AnalyticsResponse(BaseModel):
    """分析响应数据模型"""
    success: bool
    message: str
    data: Optional[AnalyticsOverview] = None
    error: Optional[str] = None
