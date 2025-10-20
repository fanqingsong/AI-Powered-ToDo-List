"""
LangGraph Agent 工具定义
包含所有任务管理相关的工具函数
"""

from langchain_core.tools import tool, BaseTool
from langgraph.errors import NodeInterrupt
from pydantic import BaseModel
from typing import List, Any, Dict
from ..services.sync_task_service import SyncTaskService


class AnyArgsSchema(BaseModel):
    """允许任意参数的前端工具模式"""
    class Config:
        extra = "allow"


class FrontendTool(BaseTool):
    """前端工具基类"""
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name=name, description=description, args_schema=AnyArgsSchema)

    def _run(self, *args, **kwargs) -> str:
        """同步执行前端工具"""
        # 前端工具应该抛出中断，让前端处理
        raise NodeInterrupt(f"Frontend tool call: {self.name}")

    async def _arun(self, *args, **kwargs) -> str:
        """异步执行前端工具"""
        # 前端工具应该抛出中断，让前端处理
        raise NodeInterrupt(f"Frontend tool call: {self.name}")


class TaskTools:
    """任务管理工具类"""
    
    def __init__(self, task_service=None):
        # 使用同步任务服务避免异步事件循环问题
        self.task_service = SyncTaskService()
        self.current_user_id = None  # 当前用户ID
        self.frontend_tools_config = []  # 前端工具配置
    
    def set_user_id(self, user_id: int):
        """设置当前用户ID"""
        self.current_user_id = user_id
    
    def set_frontend_tools_config(self, config: List[Dict[str, Any]]):
        """设置前端工具配置"""
        self.frontend_tools_config = config
    
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
        def delete_task_by_title_tool(title: str) -> str:
            """根据任务名称删除任务"""
            return self._delete_task_by_title_tool(title)
        
        @tool
        def delete_latest_task_tool() -> str:
            """删除最新的任务"""
            return self._delete_latest_task_tool()
        
        # 后端工具（实际执行）
        @tool
        def navigate_to_page_tool(page_key: str) -> str:
            """导航到指定页面"""
            return self._navigate_to_page_tool(page_key)
        
        @tool
        def refresh_task_list_tool() -> str:
            """刷新前端任务列表"""
            return self._refresh_task_list_tool()
        
        # 基础工具列表
        backend_tools = [
            create_task_tool,
            get_tasks_tool,
            get_task_tool,
            update_task_tool,
            delete_task_tool,
            delete_task_by_title_tool,
            delete_latest_task_tool,
            navigate_to_page_tool,
            refresh_task_list_tool
        ]
        
        # 添加前端工具
        frontend_tools = self._get_frontend_tools()
        
        return backend_tools + frontend_tools
    
    def _get_frontend_tools(self) -> List[FrontendTool]:
        """获取前端工具列表"""
        frontend_tools = []

        # 使用配置的前端工具或默认工具
        tools_config = self.frontend_tools_config if self.frontend_tools_config else []
        
        for tool_config in tools_config:
            frontend_tool = FrontendTool(
                name=tool_config["name"],
                description=tool_config["description"]
            )
            frontend_tools.append(frontend_tool)
        
        return frontend_tools
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """获取工具定义（用于模型绑定）"""
        tools = self.get_tools()
        tool_defs = []
        
        for tool in tools:
            if isinstance(tool, FrontendTool):
                # 前端工具定义
                tool_def = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "additionalProperties": True
                        }
                    }
                }
            else:
                # 后端工具定义
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
            
            # 任务创建成功后，触发前端刷新
            refresh_message = self._refresh_task_list_tool()
            return f'任务创建成功: "{task.title}" (ID: {task.id})\n{refresh_message}'
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
                update_data['is_complete'] = isComplete
            
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
    
    def _delete_task_by_title_tool(self, title: str) -> str:
        """根据任务名称删除任务
        
        Args:
            title: 任务名称
            
        Returns:
            删除结果信息
        """
        try:
            print(f"[DEBUG] 开始根据名称删除任务: title={title}, user_id={self.current_user_id}")
            
            # 首先查找任务
            task = self.task_service.get_task_by_title(title, self.current_user_id)
            if not task:
                print(f"[DEBUG] 未找到名称为 '{title}' 的任务")
                return f'未找到名称为 "{title}" 的任务。'
            
            # 删除任务
            deleted = self.task_service.delete_task_by_title(title, self.current_user_id)
            if not deleted:
                print(f"[DEBUG] 删除任务失败")
                return f'删除任务 "{title}" 失败。'
            
            print(f"[DEBUG] 任务删除成功: {title}")
            
            # 任务删除成功后，触发前端刷新
            refresh_message = self._refresh_task_list_tool()
            return f'任务 "{title}" 删除成功。\n{refresh_message}'
            
        except Exception as e:
            print(f"[DEBUG] 根据名称删除任务失败: {e}")
            import traceback
            traceback.print_exc()
            return f'删除任务失败: {str(e)}'
    
    def _delete_latest_task_tool(self) -> str:
        """删除最新的任务
        
        Returns:
            删除结果信息
        """
        try:
            tasks = self.task_service.get_all_tasks(self.current_user_id)
            if not tasks:
                return '没有任务可以删除。'
            
            # 获取最新的任务（假设ID最大的为最新）
            latest_task = max(tasks, key=lambda t: t.id)
            
            deleted = self.task_service.delete_task(latest_task.id, self.current_user_id)
            if not deleted:
                return f'删除任务失败。'
            
            return f'任务 {latest_task.id} ("{latest_task.title}") 删除成功。'
        except Exception as e:
            return f'删除最新任务失败: {str(e)}'
    
    def _navigate_to_page_tool(self, page_key: str) -> str:
        """导航到指定页面
        
        Args:
            page_key: 页面标识符 (settings, tasks, calendar, notes, analytics)
            
        Returns:
            页面跳转结果信息
        """
        try:
            page_mapping = {
                'settings': '系统设置',
                'tasks': '任务管理', 
                'calendar': '日程安排',
                'notes': '笔记管理',
                'analytics': '数据分析'
            }
            
            if page_key not in page_mapping:
                return f'未知的页面标识符: {page_key}。支持的页面: {", ".join(page_mapping.keys())}'
            
            page_name = page_mapping[page_key]
            print(f"[DEBUG] 页面跳转指令: {page_key} -> {page_name}")
            
            # 返回包含特殊标识的响应，前端会解析这个标识来触发页面跳转
            return f'navigate_to_{page_key} 正在为您打开{page_name}页面...'
            
        except Exception as e:
            print(f"[DEBUG] 页面跳转失败: {e}")
            return f'页面跳转失败: {str(e)}'
    
    def _refresh_task_list_tool(self) -> str:
        """刷新前端任务列表
        
        Returns:
            刷新结果信息
        """
        try:
            print("[DEBUG] 触发前端任务列表刷新")
            
            # 返回包含特殊标识的响应，前端会解析这个标识来触发任务列表刷新
            return 'frontend_tool_call:refresh_task_list 正在为您刷新任务列表...'
            
        except Exception as e:
            print(f"[DEBUG] 前端刷新失败: {e}")
            return f'前端刷新失败: {str(e)}'