from ..services import TaskService

class AgentTools:
    def __init__(self, task_service: TaskService):
        self.task_service = task_service
        self.tools = [
            self._create_task_tool()
        ]

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