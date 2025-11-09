"""
日程管理工具类
"""

from langchain_core.tools import tool
from typing import List, Any, Dict, Optional
from datetime import datetime, date
from ....services.sync_schedule_service import SyncScheduleService
from ....models.schedule import ScheduleCreate, ScheduleUpdate


class ScheduleTools:
    """日程管理工具类"""
    
    def __init__(self):
        self.schedule_service = SyncScheduleService()
        self.current_user_id = None
    
    def set_user_id(self, user_id: int):
        """设置当前用户ID"""
        self.current_user_id = user_id
    
    def get_tools(self):
        """获取所有工具"""
        @tool
        def create_schedule_tool(
            title: str,
            start_time: str,
            end_time: str,
            description: str = None,
            is_all_day: bool = False,
            location: str = None,
            color: str = "#1890ff"
        ) -> str:
            """创建新日程
            
            Args:
                title: 日程标题
                start_time: 开始时间 (ISO格式字符串，必须包含时区，如: 2024-01-02T09:00:00+08:00)
                    - 如果用户说"明天"，请使用明天的日期
                    - 如果用户说"今天"，请使用今天的日期
                    - 必须包含时区信息（UTC+8，即+08:00）
                end_time: 结束时间 (ISO格式字符串，必须包含时区，如: 2024-01-02T10:00:00+08:00)
                    - 必须与start_time在同一天，除非是跨日日程
                    - 必须包含时区信息（UTC+8，即+08:00）
                description: 日程描述（可选）
                is_all_day: 是否全天（默认False）
                location: 地点（可选）
                color: 颜色代码（默认#1890ff）
            
            重要：时间格式必须正确，包含时区信息。例如：
            - 明天09:00: 2024-01-02T09:00:00+08:00
            - 今天14:00: 2024-01-01T14:00:00+08:00
            """
            return self._create_schedule_tool(title, start_time, end_time, description, is_all_day, location, color)
        
        @tool
        def get_schedules_tool() -> str:
            """获取所有日程"""
            return self._get_schedules_tool()
        
        @tool
        def get_schedule_tool(id: int) -> str:
            """获取指定日程"""
            return self._get_schedule_tool(id)
        
        @tool
        def update_schedule_tool(
            id: int,
            title: str = None,
            start_time: str = None,
            end_time: str = None,
            description: str = None,
            is_all_day: bool = None,
            location: str = None,
            color: str = None
        ) -> str:
            """更新日程"""
            return self._update_schedule_tool(id, title, start_time, end_time, description, is_all_day, location, color)
        
        @tool
        def delete_schedule_tool(id: int) -> str:
            """删除指定日程"""
            return self._delete_schedule_tool(id)
        
        @tool
        def get_schedules_by_date_range_tool(start_date: str, end_date: str) -> str:
            """获取指定日期范围内的日程
            
            Args:
                start_date: 开始日期 (YYYY-MM-DD格式)
                end_date: 结束日期 (YYYY-MM-DD格式)
            """
            return self._get_schedules_by_date_range_tool(start_date, end_date)
        
        @tool
        def get_upcoming_schedules_tool(limit: int = 10) -> str:
            """获取即将到来的日程"""
            return self._get_upcoming_schedules_tool(limit)
        
        @tool
        def refresh_schedule_list_tool() -> str:
            """刷新前端日程列表"""
            return self._refresh_schedule_list_tool()
        
        return [
            create_schedule_tool,
            get_schedules_tool,
            get_schedule_tool,
            update_schedule_tool,
            delete_schedule_tool,
            get_schedules_by_date_range_tool,
            get_upcoming_schedules_tool,
            refresh_schedule_list_tool
        ]
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """获取工具定义（用于模型绑定）"""
        tools = self.get_tools()
        tool_defs = []
        
        for tool in tools:
            tool_def = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.args_schema.model_json_schema() if hasattr(tool, 'args_schema') else {}
                }
            }
            tool_defs.append(tool_def)
        
        return tool_defs
    
    def _create_schedule_tool(
        self,
        title: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        is_all_day: bool = False,
        location: Optional[str] = None,
        color: str = "#1890ff"
    ) -> str:
        """创建新日程"""
        try:
            # 解析时间字符串
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            schedule_data = ScheduleCreate(
                title=title,
                start_time=start_dt,
                end_time=end_dt,
                description=description,
                is_all_day=is_all_day,
                location=location,
                color=color
            )
            
            schedule = self.schedule_service.create_schedule(schedule_data, self.current_user_id)
            refresh_message = self._refresh_schedule_list_tool()
            return f'日程创建成功: "{schedule.title}" (ID: {schedule.id}, 时间: {schedule.start_time} - {schedule.end_time})\n{refresh_message}'
        except Exception as e:
            print(f"[DEBUG] 日程创建失败: {e}")
            import traceback
            traceback.print_exc()
            return f'日程创建失败: {str(e)}'
    
    def _get_schedules_tool(self) -> str:
        """获取所有日程"""
        try:
            schedules = self.schedule_service.get_all_schedules(self.current_user_id)
            if not schedules:
                return '没有找到日程。'
            
            schedule_list = '\n'.join([
                f'- {s.id}: {s.title} ({s.start_time.strftime("%Y-%m-%d %H:%M")} - {s.end_time.strftime("%H:%M")})'
                for s in schedules
            ])
            return f'找到 {len(schedules)} 个日程:\n{schedule_list}'
        except Exception as e:
            return f'获取日程列表失败: {str(e)}'
    
    def _get_schedule_tool(self, id: int) -> str:
        """获取指定日程"""
        try:
            schedule = self.schedule_service.get_schedule_by_id(id, self.current_user_id)
            if not schedule:
                return f'未找到 ID 为 {id} 的日程。'
            
            return f'日程 {schedule.id}: "{schedule.title}"\n时间: {schedule.start_time} - {schedule.end_time}\n描述: {schedule.description or "无"}'
        except Exception as e:
            return f'获取日程失败: {str(e)}'
    
    def _update_schedule_tool(
        self,
        id: int,
        title: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        description: Optional[str] = None,
        is_all_day: Optional[bool] = None,
        location: Optional[str] = None,
        color: Optional[str] = None
    ) -> str:
        """更新日程"""
        try:
            update_data = {}
            if title is not None:
                update_data['title'] = title
            if start_time is not None:
                update_data['start_time'] = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if end_time is not None:
                update_data['end_time'] = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            if description is not None:
                update_data['description'] = description
            if is_all_day is not None:
                update_data['is_all_day'] = is_all_day
            if location is not None:
                update_data['location'] = location
            if color is not None:
                update_data['color'] = color
            
            if not update_data:
                return '没有提供要更新的字段。'
            
            schedule_update = ScheduleUpdate(**update_data)
            updated_schedule = self.schedule_service.update_schedule(id, schedule_update, self.current_user_id)
            
            if not updated_schedule:
                return f'更新日程 {id} 失败。'
            
            refresh_message = self._refresh_schedule_list_tool()
            return f'日程 {updated_schedule.id} 更新成功: "{updated_schedule.title}"\n{refresh_message}'
        except Exception as e:
            return f'更新日程失败: {str(e)}'
    
    def _delete_schedule_tool(self, id: int) -> str:
        """删除指定日程"""
        try:
            schedule = self.schedule_service.get_schedule_by_id(id, self.current_user_id)
            if not schedule:
                return f'未找到 ID 为 {id} 的日程。'
            
            deleted = self.schedule_service.delete_schedule(id, self.current_user_id)
            if not deleted:
                return f'删除日程 {id} 失败。'
            
            refresh_message = self._refresh_schedule_list_tool()
            return f'日程 {schedule.id} ("{schedule.title}") 删除成功。\n{refresh_message}'
        except Exception as e:
            return f'删除日程失败: {str(e)}'
    
    def _get_schedules_by_date_range_tool(self, start_date: str, end_date: str) -> str:
        """获取指定日期范围内的日程"""
        try:
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)
            
            schedules = self.schedule_service.get_schedules_by_date_range(start, end, self.current_user_id)
            if not schedules:
                return f'在 {start_date} 到 {end_date} 之间没有找到日程。'
            
            schedule_list = '\n'.join([
                f'- {s.id}: {s.title} ({s.start_time.strftime("%Y-%m-%d %H:%M")} - {s.end_time.strftime("%H:%M")})'
                for s in schedules
            ])
            return f'找到 {len(schedules)} 个日程:\n{schedule_list}'
        except Exception as e:
            return f'获取日程失败: {str(e)}'
    
    def _get_upcoming_schedules_tool(self, limit: int = 10) -> str:
        """获取即将到来的日程"""
        try:
            schedules = self.schedule_service.get_upcoming_schedules(limit, self.current_user_id)
            if not schedules:
                return '没有即将到来的日程。'
            
            schedule_list = '\n'.join([
                f'- {s.id}: {s.title} ({s.start_time.strftime("%Y-%m-%d %H:%M")} - {s.end_time.strftime("%H:%M")})'
                for s in schedules
            ])
            return f'找到 {len(schedules)} 个即将到来的日程:\n{schedule_list}'
        except Exception as e:
            return f'获取即将到来的日程失败: {str(e)}'
    
    def _refresh_schedule_list_tool(self) -> str:
        """刷新前端日程列表"""
        try:
            return 'frontend_tool_call:refresh_schedule_list 正在为您刷新日程列表...'
        except Exception as e:
            return f'前端刷新失败: {str(e)}'

