from typing import Optional 
from ..services import TaskService

class AgentTools:
    def __init__(self, task_service: TaskService):
        self.task_service = task_service

    def _create_task_tool(self):
        async def create_task(title: str, isComplete: bool = False) -> str:
            """
            Create a new task.

            :param title: the title of the new task.
            :param isComplete: the status of the task. When this value is true, it means that the task is completed.
            :return: task information as a string.
            """ 
            task = await self.task_service.add_task(title, isComplete)
            return f'Task created successfully: "{task.title}" (ID: {task.id})'
        
        return create_task  
    
    def _get_tasks_tool(self):
        async def get_tasks() -> str:
            """
            Get all tasks.

            :return: list of tasks as a string.
            """ 
            tasks = await self.task_service.get_all_tasks()
            if not tasks:
                return 'No tasks found.'
            
            task_list = '\n'.join([
                f'- {t.id}: {t.title} ({"Complete" if t.isComplete else "Incomplete"})'
                for t in tasks
            ])
            return f'Found {len(tasks)} tasks:\n{task_list}'
        return get_tasks
    
    def _get_task_tool(self):
        async def get_task(id: int) -> str:
            """
            Get one specific task with id.

            :param id: the id of the target task.
            :return: task information as a string.
            """ 
            task = await self.task_service.get_task_by_id(id)
            if not task:
                return f'Task with ID {id} not found.'
            
            status = "Complete" if task.isComplete else "Incomplete"
            return f'Task {task.id}: "{task.title}" - Status: {status}'
        
        return get_task
    
    def _update_task_tool(self):
        async def update_task(id: int, title: Optional[str] = None, isComplete: Optional[bool] = None) -> str:
            """
            Update a specific task with its id, its new title and its new complete status.

            :param id: the id of the target task.
            :param title: the new title of the target task. This parameter is optional.
            :param isComplete: the new complete status of the target task. This parameter is optional.
            :return: a string to show that the task update action is finished. It may success or fail.
            """ 
            updated = await self.task_service.update_task(id, title, isComplete)
            if not updated:
                return f'Task with ID {id} not found.'
            return f'Task {id} updated successfully.'
        
        return update_task
    
    def _delete_task_tool(self):
        async def delete_task(id: int) -> str:
            """
            Delete one specific task with id.

            :param id: the id of the target task.
            :return: a string to show that the task delete action is finished. It may success or fail.
            """ 
            deleted = await self.task_service.delete_task(id)
            if not deleted:
                return f'Task with ID {id} not found.'
            return f'Task {id} deleted successfully.'
        
        return delete_task    