"""
LangGraph Agent 工具定义
包含所有任务管理相关的工具函数
"""

from langchain_core.tools import tool
from typing import List
from ..services.sync_task_service import SyncTaskService


class TaskTools:
    """任务管理工具类"""
    
    def __init__(self, task_service=None):
        # 使用同步任务服务避免异步事件循环问题
        self.task_service = SyncTaskService()
        self.current_user_id = None  # 当前用户ID
    
    def set_user_id(self, user_id: int):
        """设置当前用户ID"""
        self.current_user_id = user_id
    
    def get_tools(self):
        """获取所有工具"""
        # 创建包装函数来避免 self 参数问题
        @tool
        def create_task_tool(title: str, isComplete: bool = False) -> str:
            """创建新任务"""
            return self._create_task_tool(title, isComplete)
        
        @tool
        def get_tasks_tool() -> str:
            """获取所有任务"""
            return self._get_tasks_tool()
        
        @tool
        def get_task_tool(id: int) -> str:
            """获取指定任务"""
            return self._get_task_tool(id)
        
        @tool
        def update_task_tool(id: int, title: str = None, isComplete: bool = None) -> str:
            """更新任务"""
            return self._update_task_tool(id, title, isComplete)
        
        @tool
        def delete_task_tool(id: int) -> str:
            """删除指定任务"""
            return self._delete_task_tool(id)
        
        @tool
        def delete_latest_task_tool() -> str:
            """删除最新的任务"""
            return self._delete_latest_task_tool()
        
        return [
            create_task_tool,
            get_tasks_tool,
            get_task_tool,
            update_task_tool,
            delete_task_tool,
            delete_latest_task_tool
        ]
    
    def _create_task_tool(self, title: str, isComplete: bool = False) -> str:
        """创建新任务
        
        Args:
            title: 任务标题
            isComplete: 任务是否完成，默认为 False
            
        Returns:
            任务创建结果信息
        """
        try:
            print(f"[DEBUG] 开始创建任务: title={title}, isComplete={isComplete}, user_id={self.current_user_id}")
            task = self.task_service.add_task(title, isComplete, self.current_user_id)
            print(f"[DEBUG] 任务创建成功: {task.title} (ID: {task.id})")
            return f'任务创建成功: "{task.title}" (ID: {task.id})'
        except Exception as e:
            print(f"[DEBUG] 任务创建失败: {e}")
            import traceback
            traceback.print_exc()
            return f'任务创建失败: {str(e)}'
    
    def _get_tasks_tool(self) -> str:
        """获取所有任务
        
        Returns:
            任务列表信息
        """
        try:
            print(f"[DEBUG] 开始获取任务列表, user_id={self.current_user_id}")
            tasks = self.task_service.get_all_tasks(self.current_user_id)
            if not tasks:
                print("[DEBUG] 没有找到任务")
                return '没有找到任务。'
            
            task_list = '\n'.join([
                f'- {t.id}: {t.title} ({"已完成" if t.isComplete else "未完成"})'
                for t in tasks
            ])
            print(f"[DEBUG] 找到 {len(tasks)} 个任务")
            return f'找到 {len(tasks)} 个任务:\n{task_list}'
        except Exception as e:
            print(f"[DEBUG] 获取任务列表失败: {e}")
            import traceback
            traceback.print_exc()
            return f'获取任务列表失败: {str(e)}'
    
    def _get_task_tool(self, id: int) -> str:
        """获取指定任务
        
        Args:
            id: 任务ID
            
        Returns:
            任务信息
        """
        try:
            task = self.task_service.get_task_by_id(id)
            if not task:
                return f'未找到 ID 为 {id} 的任务。'
            
            status = "已完成" if task.isComplete else "未完成"
            return f'任务 {task.id}: "{task.title}" - {status}'
        except Exception as e:
            return f'获取任务失败: {str(e)}'
    
    def _update_task_tool(self, id: int, title: str = None, isComplete: bool = None) -> str:
        """更新任务
        
        Args:
            id: 任务ID
            title: 新的任务标题（可选）
            isComplete: 新的完成状态（可选）
            
        Returns:
            更新结果信息
        """
        try:
            task = self.task_service.get_task_by_id(id)
            if not task:
                return f'未找到 ID 为 {id} 的任务。'
            
            # 构建更新数据
            update_data = {}
            if title is not None:
                update_data['title'] = title
            if isComplete is not None:
                update_data['isComplete'] = isComplete
            
            if not update_data:
                return '没有提供要更新的字段。'
            
            updated_task = self.task_service.update_task(id, **update_data)
            if not updated_task:
                return f'更新任务 {id} 失败。'
            
            status = "已完成" if updated_task.isComplete else "未完成"
            return f'任务 {updated_task.id} 更新成功: "{updated_task.title}" - {status}'
        except Exception as e:
            return f'更新任务失败: {str(e)}'
    
    def _delete_task_tool(self, id: int) -> str:
        """删除指定任务
        
        Args:
            id: 任务ID
            
        Returns:
            删除结果信息
        """
        try:
            task = self.task_service.get_task_by_id(id)
            if not task:
                return f'未找到 ID 为 {id} 的任务。'
            
            deleted = self.task_service.delete_task(id)
            if not deleted:
                return f'删除任务 {id} 失败。'
            
            return f'任务 {task.id} ("{task.title}") 删除成功。'
        except Exception as e:
            return f'删除任务失败: {str(e)}'
    
    def _delete_latest_task_tool(self) -> str:
        """删除最新的任务
        
        Returns:
            删除结果信息
        """
        try:
            tasks = self.task_service.get_all_tasks()
            if not tasks:
                return '没有任务可以删除。'
            
            # 获取最新的任务（假设ID最大的为最新）
            latest_task = max(tasks, key=lambda t: t.id)
            
            deleted = self.task_service.delete_task(latest_task.id)
            if not deleted:
                return f'删除任务失败。'
            
            return f'任务 {latest_task.id} ("{latest_task.title}") 删除成功。'
        except Exception as e:
            return f'删除最新任务失败: {str(e)}'