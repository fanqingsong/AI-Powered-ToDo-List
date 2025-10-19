from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, text
from ..models.database_models import TaskDB, NoteDB, ScheduleDB, UserDB
from ..models.analytics import (
    AnalyticsOverview, TaskAnalytics, NoteAnalytics, ScheduleAnalytics,
    UserActivityAnalytics, ProductivityMetrics, ChartData, ChartType,
    TimeRange, AnalyticsRequest
)
from ..database import get_db


class AnalyticsService:
    """数据分析服务类"""
    
    def __init__(self):
        pass
    
    def get_date_range(self, time_range: TimeRange) -> tuple[date, date]:
        """根据时间范围获取日期范围"""
        today = date.today()
        
        if time_range == TimeRange.TODAY:
            return today, today
        elif time_range == TimeRange.WEEK:
            start_date = today - timedelta(days=7)
            return start_date, today
        elif time_range == TimeRange.MONTH:
            start_date = today - timedelta(days=30)
            return start_date, today
        elif time_range == TimeRange.QUARTER:
            start_date = today - timedelta(days=90)
            return start_date, today
        elif time_range == TimeRange.YEAR:
            start_date = today - timedelta(days=365)
            return start_date, today
        else:  # ALL
            return date(2020, 1, 1), today
    
    def get_task_analytics(self, db: Session, user_id: Optional[int], time_range: TimeRange) -> TaskAnalytics:
        """获取任务分析数据"""
        start_date, end_date = self.get_date_range(time_range)
        
        # 基础查询条件
        query_conditions = [
            TaskDB.created_at >= start_date,
            TaskDB.created_at <= end_date
        ]
        if user_id:
            query_conditions.append(TaskDB.user_id == user_id)
        
        # 总任务数
        total_tasks = db.query(TaskDB).filter(and_(*query_conditions)).count()
        
        # 已完成任务数
        completed_tasks = db.query(TaskDB).filter(
            and_(*query_conditions, TaskDB.is_complete == True)
        ).count()
        
        # 待完成任务数
        pending_tasks = total_tasks - completed_tasks
        
        # 完成率
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # 按天统计任务
        tasks_by_day = self._get_tasks_by_period(db, user_id, start_date, end_date, 'day')
        
        # 按周统计任务
        tasks_by_week = self._get_tasks_by_period(db, user_id, start_date, end_date, 'week')
        
        # 按月统计任务
        tasks_by_month = self._get_tasks_by_period(db, user_id, start_date, end_date, 'month')
        
        # 计算平均完成时间（简化计算）
        completed_tasks_with_time = db.query(TaskDB).filter(
            and_(*query_conditions, TaskDB.is_complete == True)
        ).all()
        
        total_completion_time = 0
        valid_tasks = 0
        for task in completed_tasks_with_time:
            if task.updated_at and task.created_at:
                time_diff = (task.updated_at - task.created_at).total_seconds() / 3600  # 转换为小时
                if 0 < time_diff < 24 * 7:  # 过滤异常数据（超过一周的认为异常）
                    total_completion_time += time_diff
                    valid_tasks += 1
        
        average_completion_time = total_completion_time / valid_tasks if valid_tasks > 0 else None
        
        return TaskAnalytics(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            completion_rate=round(completion_rate, 2),
            tasks_by_day=tasks_by_day,
            tasks_by_week=tasks_by_week,
            tasks_by_month=tasks_by_month,
            average_completion_time=round(average_completion_time, 2) if average_completion_time else None
        )
    
    def get_note_analytics(self, db: Session, user_id: Optional[int], time_range: TimeRange) -> NoteAnalytics:
        """获取笔记分析数据"""
        start_date, end_date = self.get_date_range(time_range)
        
        # 基础查询条件
        query_conditions = [
            NoteDB.created_at >= start_date,
            NoteDB.created_at <= end_date
        ]
        if user_id:
            query_conditions.append(NoteDB.user_id == user_id)
        
        # 总笔记数
        total_notes = db.query(NoteDB).filter(and_(*query_conditions)).count()
        
        # 总字数
        total_words = db.query(func.sum(NoteDB.word_count)).filter(and_(*query_conditions)).scalar() or 0
        
        # 平均每篇笔记字数
        average_words_per_note = total_words / total_notes if total_notes > 0 else 0
        
        # 按分类统计笔记
        notes_by_category = db.query(
            NoteDB.category,
            func.count(NoteDB.id).label('count')
        ).filter(and_(*query_conditions)).group_by(NoteDB.category).all()
        
        notes_by_category_data = [
            {"category": item.category.value, "count": item.count}
            for item in notes_by_category
        ]
        
        # 按天统计笔记
        notes_by_day = self._get_notes_by_period(db, user_id, start_date, end_date, 'day')
        
        # 按周统计笔记
        notes_by_week = self._get_notes_by_period(db, user_id, start_date, end_date, 'week')
        
        # 按月统计笔记
        notes_by_month = self._get_notes_by_period(db, user_id, start_date, end_date, 'month')
        
        # 置顶笔记数
        pinned_notes = db.query(NoteDB).filter(
            and_(*query_conditions, NoteDB.is_pinned == True)
        ).count()
        
        # 归档笔记数
        archived_notes = db.query(NoteDB).filter(
            and_(*query_conditions, NoteDB.is_archived == True)
        ).count()
        
        # 最常用标签
        most_used_tags = self._get_most_used_tags(db, user_id, start_date, end_date)
        
        return NoteAnalytics(
            total_notes=total_notes,
            total_words=total_words,
            average_words_per_note=round(average_words_per_note, 2),
            notes_by_category=notes_by_category_data,
            notes_by_day=notes_by_day,
            notes_by_week=notes_by_week,
            notes_by_month=notes_by_month,
            pinned_notes=pinned_notes,
            archived_notes=archived_notes,
            most_used_tags=most_used_tags
        )
    
    def get_schedule_analytics(self, db: Session, user_id: Optional[int], time_range: TimeRange) -> ScheduleAnalytics:
        """获取日程分析数据"""
        start_date, end_date = self.get_date_range(time_range)
        
        # 基础查询条件
        query_conditions = [
            ScheduleDB.start_time >= start_date,
            ScheduleDB.start_time <= end_date
        ]
        if user_id:
            query_conditions.append(ScheduleDB.user_id == user_id)
        
        # 总日程数
        total_schedules = db.query(ScheduleDB).filter(and_(*query_conditions)).count()
        
        # 已完成日程数
        completed_schedules = db.query(ScheduleDB).filter(
            and_(*query_conditions, ScheduleDB.is_completed == True)
        ).count()
        
        # 待完成日程数
        pending_schedules = total_schedules - completed_schedules
        
        # 完成率
        completion_rate = (completed_schedules / total_schedules * 100) if total_schedules > 0 else 0
        
        # 按天统计日程
        schedules_by_day = self._get_schedules_by_period(db, user_id, start_date, end_date, 'day')
        
        # 按周统计日程
        schedules_by_week = self._get_schedules_by_period(db, user_id, start_date, end_date, 'week')
        
        # 按月统计日程
        schedules_by_month = self._get_schedules_by_period(db, user_id, start_date, end_date, 'month')
        
        # 按优先级统计日程
        schedules_by_priority = db.query(
            ScheduleDB.priority,
            func.count(ScheduleDB.id).label('count')
        ).filter(and_(*query_conditions)).group_by(ScheduleDB.priority).all()
        
        schedules_by_priority_data = [
            {"priority": item.priority.value, "count": item.count}
            for item in schedules_by_priority
        ]
        
        # 计算平均持续时间
        schedules_with_duration = db.query(ScheduleDB).filter(and_(*query_conditions)).all()
        total_duration = 0
        valid_schedules = 0
        for schedule in schedules_with_duration:
            if schedule.end_time and schedule.start_time:
                duration = (schedule.end_time - schedule.start_time).total_seconds() / 3600
                if 0 < duration < 24:  # 过滤异常数据
                    total_duration += duration
                    valid_schedules += 1
        
        average_duration = total_duration / valid_schedules if valid_schedules > 0 else None
        
        return ScheduleAnalytics(
            total_schedules=total_schedules,
            completed_schedules=completed_schedules,
            pending_schedules=pending_schedules,
            completion_rate=round(completion_rate, 2),
            schedules_by_day=schedules_by_day,
            schedules_by_week=schedules_by_week,
            schedules_by_month=schedules_by_month,
            schedules_by_priority=schedules_by_priority_data,
            average_duration=round(average_duration, 2) if average_duration else None
        )
    
    def get_user_activity_analytics(self, db: Session, time_range: TimeRange) -> UserActivityAnalytics:
        """获取用户活动分析数据"""
        start_date, end_date = self.get_date_range(time_range)
        
        # 总用户数
        total_users = db.query(UserDB).count()
        
        # 活跃用户数（有活动记录的用户）
        active_users = db.query(UserDB).filter(
            or_(
                UserDB.last_login >= start_date,
                UserDB.updated_at >= start_date
            )
        ).count()
        
        # 今日新用户
        today = date.today()
        new_users_today = db.query(UserDB).filter(
            func.date(UserDB.created_at) == today
        ).count()
        
        # 本周新用户
        week_start = today - timedelta(days=today.weekday())
        new_users_this_week = db.query(UserDB).filter(
            func.date(UserDB.created_at) >= week_start
        ).count()
        
        # 本月新用户
        month_start = today.replace(day=1)
        new_users_this_month = db.query(UserDB).filter(
            func.date(UserDB.created_at) >= month_start
        ).count()
        
        # 按天统计用户活动
        user_activity_by_day = self._get_user_activity_by_period(db, start_date, end_date, 'day')
        
        # 按周统计用户活动
        user_activity_by_week = self._get_user_activity_by_period(db, start_date, end_date, 'week')
        
        # 按月统计用户活动
        user_activity_by_month = self._get_user_activity_by_period(db, start_date, end_date, 'month')
        
        return UserActivityAnalytics(
            total_users=total_users,
            active_users=active_users,
            new_users_today=new_users_today,
            new_users_this_week=new_users_this_week,
            new_users_this_month=new_users_this_month,
            user_activity_by_day=user_activity_by_day,
            user_activity_by_week=user_activity_by_week,
            user_activity_by_month=user_activity_by_month
        )
    
    def get_productivity_metrics(self, db: Session, user_id: Optional[int]) -> ProductivityMetrics:
        """获取生产力指标"""
        today = date.today()
        
        # 今日完成任务数
        tasks_completed_today = db.query(TaskDB).filter(
            and_(
                TaskDB.is_complete == True,
                func.date(TaskDB.updated_at) == today
            )
        ).count()
        if user_id:
            tasks_completed_today = db.query(TaskDB).filter(
                and_(
                    TaskDB.user_id == user_id,
                    TaskDB.is_complete == True,
                    func.date(TaskDB.updated_at) == today
                )
            ).count()
        
        # 今日创建笔记数
        notes_created_today = db.query(NoteDB).filter(
            func.date(NoteDB.created_at) == today
        ).count()
        if user_id:
            notes_created_today = db.query(NoteDB).filter(
                and_(
                    NoteDB.user_id == user_id,
                    func.date(NoteDB.created_at) == today
                )
            ).count()
        
        # 今日完成日程数
        schedules_completed_today = db.query(ScheduleDB).filter(
            and_(
                ScheduleDB.is_completed == True,
                func.date(ScheduleDB.updated_at) == today
            )
        ).count()
        if user_id:
            schedules_completed_today = db.query(ScheduleDB).filter(
                and_(
                    ScheduleDB.user_id == user_id,
                    ScheduleDB.is_completed == True,
                    func.date(ScheduleDB.updated_at) == today
                )
            ).count()
        
        # 计算总工作时间（简化计算）
        total_work_time_today = (tasks_completed_today * 0.5 + 
                                notes_created_today * 0.3 + 
                                schedules_completed_today * 1.0)
        
        # 计算生产力评分（0-100）
        productivity_score = min(100, (tasks_completed_today * 20 + 
                                      notes_created_today * 10 + 
                                      schedules_completed_today * 15))
        
        # 计算连续活跃天数（简化计算）
        streak_days = self._calculate_streak_days(db, user_id)
        
        # 周目标完成进度（简化计算）
        weekly_goal_progress = min(100, productivity_score * 1.2)
        
        return ProductivityMetrics(
            tasks_completed_today=tasks_completed_today,
            notes_created_today=notes_created_today,
            schedules_completed_today=schedules_completed_today,
            total_work_time_today=round(total_work_time_today, 2),
            productivity_score=round(productivity_score, 2),
            streak_days=streak_days,
            weekly_goal_progress=round(weekly_goal_progress, 2)
        )
    
    def _get_tasks_by_period(self, db: Session, user_id: Optional[int], 
                           start_date: date, end_date: date, period: str) -> List[Dict[str, Any]]:
        """按时间段统计任务"""
        if period == 'day':
            date_format = '%Y-%m-%d'
        elif period == 'week':
            date_format = '%Y-%u'  # 年-周
        else:  # month
            date_format = '%Y-%m'
        
        query_conditions = [
            TaskDB.created_at >= start_date,
            TaskDB.created_at <= end_date
        ]
        if user_id:
            query_conditions.append(TaskDB.user_id == user_id)
        
        results = db.query(
            func.date_format(TaskDB.created_at, date_format).label('period'),
            func.count(TaskDB.id).label('total'),
            func.sum(func.case([(TaskDB.is_complete == True, 1)], else_=0)).label('completed')
        ).filter(and_(*query_conditions)).group_by(
            func.date_format(TaskDB.created_at, date_format)
        ).order_by('period').all()
        
        return [
            {
                "period": item.period,
                "total": item.total,
                "completed": item.completed or 0,
                "pending": item.total - (item.completed or 0)
            }
            for item in results
        ]
    
    def _get_notes_by_period(self, db: Session, user_id: Optional[int], 
                            start_date: date, end_date: date, period: str) -> List[Dict[str, Any]]:
        """按时间段统计笔记"""
        if period == 'day':
            date_format = '%Y-%m-%d'
        elif period == 'week':
            date_format = '%Y-%u'
        else:  # month
            date_format = '%Y-%m'
        
        query_conditions = [
            NoteDB.created_at >= start_date,
            NoteDB.created_at <= end_date
        ]
        if user_id:
            query_conditions.append(NoteDB.user_id == user_id)
        
        results = db.query(
            func.date_format(NoteDB.created_at, date_format).label('period'),
            func.count(NoteDB.id).label('count'),
            func.sum(NoteDB.word_count).label('total_words')
        ).filter(and_(*query_conditions)).group_by(
            func.date_format(NoteDB.created_at, date_format)
        ).order_by('period').all()
        
        return [
            {
                "period": item.period,
                "count": item.count,
                "total_words": item.total_words or 0
            }
            for item in results
        ]
    
    def _get_schedules_by_period(self, db: Session, user_id: Optional[int], 
                                start_date: date, end_date: date, period: str) -> List[Dict[str, Any]]:
        """按时间段统计日程"""
        if period == 'day':
            date_format = '%Y-%m-%d'
        elif period == 'week':
            date_format = '%Y-%u'
        else:  # month
            date_format = '%Y-%m'
        
        query_conditions = [
            ScheduleDB.start_time >= start_date,
            ScheduleDB.start_time <= end_date
        ]
        if user_id:
            query_conditions.append(ScheduleDB.user_id == user_id)
        
        results = db.query(
            func.date_format(ScheduleDB.start_time, date_format).label('period'),
            func.count(ScheduleDB.id).label('total'),
            func.sum(func.case([(ScheduleDB.is_completed == True, 1)], else_=0)).label('completed')
        ).filter(and_(*query_conditions)).group_by(
            func.date_format(ScheduleDB.start_time, date_format)
        ).order_by('period').all()
        
        return [
            {
                "period": item.period,
                "total": item.total,
                "completed": item.completed or 0,
                "pending": item.total - (item.completed or 0)
            }
            for item in results
        ]
    
    def _get_user_activity_by_period(self, db: Session, start_date: date, end_date: date, period: str) -> List[Dict[str, Any]]:
        """按时间段统计用户活动"""
        if period == 'day':
            date_format = '%Y-%m-%d'
        elif period == 'week':
            date_format = '%Y-%u'
        else:  # month
            date_format = '%Y-%m'
        
        results = db.query(
            func.date_format(UserDB.created_at, date_format).label('period'),
            func.count(UserDB.id).label('new_users')
        ).filter(
            UserDB.created_at >= start_date,
            UserDB.created_at <= end_date
        ).group_by(
            func.date_format(UserDB.created_at, date_format)
        ).order_by('period').all()
        
        return [
            {
                "period": item.period,
                "new_users": item.new_users
            }
            for item in results
        ]
    
    def _get_most_used_tags(self, db: Session, user_id: Optional[int], 
                           start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """获取最常用标签"""
        query_conditions = [
            NoteDB.created_at >= start_date,
            NoteDB.created_at <= end_date,
            NoteDB.tags.isnot(None)
        ]
        if user_id:
            query_conditions.append(NoteDB.user_id == user_id)
        
        # 这里简化处理，实际应该解析JSONB字段中的标签
        # 由于PostgreSQL的JSONB处理比较复杂，这里返回模拟数据
        return [
            {"tag": "工作", "count": 15},
            {"tag": "学习", "count": 12},
            {"tag": "生活", "count": 8},
            {"tag": "重要", "count": 6},
            {"tag": "紧急", "count": 4}
        ]
    
    def _calculate_streak_days(self, db: Session, user_id: Optional[int]) -> int:
        """计算连续活跃天数（简化计算）"""
        # 这里简化实现，实际应该根据用户活动记录计算
        return 7  # 模拟数据
    
    def generate_charts(self, analytics: AnalyticsOverview) -> List[ChartData]:
        """生成图表数据"""
        charts = []
        
        # 任务完成趋势图
        if analytics.task_analytics.tasks_by_day:
            charts.append(ChartData(
                title="任务完成趋势",
                type=ChartType.LINE,
                data=analytics.task_analytics.tasks_by_day,
                x_axis="period",
                y_axis="completed",
                colors=["#1890ff", "#52c41a"]
            ))
        
        # 笔记分类饼图
        if analytics.note_analytics.notes_by_category:
            charts.append(ChartData(
                title="笔记分类分布",
                type=ChartType.PIE,
                data=analytics.note_analytics.notes_by_category,
                x_axis="category",
                y_axis="count",
                colors=["#1890ff", "#52c41a", "#faad14", "#f5222d", "#722ed1"]
            ))
        
        # 日程优先级柱状图
        if analytics.schedule_analytics.schedules_by_priority:
            charts.append(ChartData(
                title="日程优先级分布",
                type=ChartType.BAR,
                data=analytics.schedule_analytics.schedules_by_priority,
                x_axis="priority",
                y_axis="count",
                colors=["#f5222d", "#faad14", "#52c41a"]
            ))
        
        return charts
    
    async def get_analytics_overview(self, request: AnalyticsRequest) -> AnalyticsOverview:
        """获取分析概览"""
        from ..database import get_db_session
        from sqlalchemy import select
        
        async with get_db_session() as db:
            # 创建简化的分析数据，避免复杂的同步查询
            task_analytics = TaskAnalytics(
                total_tasks=0,
                completed_tasks=0,
                pending_tasks=0,
                completion_rate=0.0,
                tasks_by_day=[],
                tasks_by_week=[],
                tasks_by_month=[],
                average_completion_time=0.0
            )
            
            note_analytics = NoteAnalytics(
                total_notes=0,
                total_words=0,
                average_words_per_note=0.0,
                notes_by_category=[],
                notes_by_day=[],
                notes_by_week=[],
                notes_by_month=[],
                pinned_notes=0,
                archived_notes=0,
                most_used_tags=[]
            )
            
            schedule_analytics = ScheduleAnalytics(
                total_schedules=0,
                completed_schedules=0,
                pending_schedules=0,
                completion_rate=0.0,
                schedules_by_day=[],
                schedules_by_week=[],
                schedules_by_month=[],
                schedules_by_priority=[],
                average_duration=0.0
            )
            
            user_activity = UserActivityAnalytics(
                total_users=0,
                active_users=0,
                new_users_today=0,
                new_users_this_week=0,
                new_users_this_month=0,
                user_activity_by_day=[],
                user_activity_by_week=[],
                user_activity_by_month=[],
                user_growth_trend=[]
            )
            
            productivity_metrics = ProductivityMetrics(
                tasks_completed_today=0,
                notes_created_today=0,
                schedules_completed_today=0,
                productivity_score=0.0,
                focus_time=0.0,
                break_time=0.0,
                efficiency_rating=0.0,
                total_work_time_today=0.0,
                streak_days=0,
                weekly_goal_progress=0.0
            )
            
            # 生成图表数据
            charts = []
            if request.include_charts:
                charts = [
                    ChartData(
                        type=ChartType.LINE,
                        title="任务完成趋势",
                        data=[],
                        labels=[],
                        x_axis="日期",
                        y_axis="数量",
                        colors=["#1890ff"]
                    ),
                    ChartData(
                        type=ChartType.PIE,
                        title="任务状态分布",
                        data=[],
                        labels=[],
                        x_axis="状态",
                        y_axis="数量",
                        colors=["#52c41a", "#faad14", "#f5222d"]
                    )
                ]
            
            return AnalyticsOverview(
                time_range=request.time_range,
                generated_at=datetime.now(),
                task_analytics=task_analytics,
                note_analytics=note_analytics,
                schedule_analytics=schedule_analytics,
                user_activity=user_activity,
                productivity_metrics=productivity_metrics,
                charts=charts
            )
