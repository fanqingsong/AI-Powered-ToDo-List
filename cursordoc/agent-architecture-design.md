# Agent 架构设计文档

## 概述

本文档描述了支持三类资源（任务、日程、笔记）管理的 Agent 架构设计。新的架构将原来只支持任务管理的 Agent 扩展为支持多资源类型的统一管理 Agent。

## 架构设计

### 1. 核心组件

#### 1.1 同步服务层（Sync Services）

为了避免异步事件循环问题，为每类资源创建了同步版本的服务：

- **SyncTaskService** (`backend/src/services/sync_task_service.py`)
  - 已存在，用于任务管理

- **SyncScheduleService** (`backend/src/services/sync_schedule_service.py`)
  - 新增，用于日程管理的同步服务
  - 提供创建、查询、更新、删除日程的功能
  - 支持按日期范围查询和获取即将到来的日程

- **SyncNoteService** (`backend/src/services/sync_note_service.py`)
  - 新增，用于笔记管理的同步服务
  - 提供创建、查询、更新、删除笔记的功能
  - 支持搜索、置顶、归档等高级功能

#### 1.2 工具类（Tools）

每类资源都有对应的工具类，封装了 Agent 可以调用的操作：

- **TaskTools** (`backend/src/agents/task_tools.py`)
  - 已存在，提供任务管理工具
  - 包括：创建任务、获取任务、更新任务、删除任务等

- **ScheduleTools** (`backend/src/agents/schedule_tools.py`)
  - 新增，提供日程管理工具
  - 包括：
    - `create_schedule_tool`: 创建日程
    - `get_schedules_tool`: 获取所有日程
    - `get_schedule_tool`: 获取指定日程
    - `update_schedule_tool`: 更新日程
    - `delete_schedule_tool`: 删除日程
    - `get_schedules_by_date_range_tool`: 按日期范围查询
    - `get_upcoming_schedules_tool`: 获取即将到来的日程
    - `refresh_schedule_list_tool`: 刷新前端日程列表

- **NoteTools** (`backend/src/agents/note_tools.py`)
  - 新增，提供笔记管理工具
  - 包括：
    - `create_note_tool`: 创建笔记
    - `get_notes_tool`: 获取所有笔记
    - `get_note_tool`: 获取指定笔记
    - `update_note_tool`: 更新笔记
    - `delete_note_tool`: 删除笔记
    - `search_notes_tool`: 搜索笔记
    - `get_pinned_notes_tool`: 获取置顶笔记
    - `get_recent_notes_tool`: 获取最近笔记
    - `refresh_note_list_tool`: 刷新前端笔记列表

#### 1.3 统一工具管理器（ResourceToolsManager）

**ResourceToolsManager** (`backend/src/agents/resource_tools_manager.py`) 是核心的统一管理器：

- 统一管理三类资源的工具
- 提供统一的接口设置用户ID和前端工具配置
- 合并所有工具定义，供 Agent 使用

```python
class ResourceToolsManager:
    def __init__(self):
        self.task_tools = TaskTools()
        self.schedule_tools = ScheduleTools()
        self.note_tools = NoteTools()
    
    def get_tools(self) -> List:
        """获取所有工具（任务、日程、笔记）"""
        ...
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """获取所有工具定义（用于模型绑定）"""
        ...
```

### 2. Agent 架构更新

#### 2.1 Agent Graph (`backend/src/agents/agent.py`)

- 更新为使用 `ResourceToolsManager` 而不是 `TaskTools`
- 保持原有的 LangGraph 工作流结构
- 支持所有三类资源的工具调用

#### 2.2 Agent Wrapper (`backend/src/agents/agent_wrapper.py`)

- `TaskManagementAgent` 类更新为使用 `ResourceToolsManager`
- 保持向后兼容的 API 接口
- 支持流式处理和前端工具调用

#### 2.3 系统提示词 (`backend/src/agents/prompt.py`)

- 更新系统提示词模板，说明支持三类资源
- `generate_dynamic_system_prompt` 函数更新为：
  - 优先使用 `resource_tools_manager`
  - 保持对 `task_tools` 的向后兼容
  - 按资源类型分组显示工具描述

## 工具功能列表

### 任务管理工具
- `create_task_tool`: 创建新任务
- `get_tasks_tool`: 获取所有任务
- `get_task_tool`: 获取指定任务
- `update_task_tool`: 更新任务
- `delete_task_tool`: 删除指定任务
- `delete_task_by_title_tool`: 根据任务名称删除任务
- `delete_latest_task_tool`: 删除最新的任务
- `navigate_to_page_tool`: 导航到指定页面
- `refresh_task_list_tool`: 刷新前端任务列表

### 日程管理工具
- `create_schedule_tool`: 创建新日程
- `get_schedules_tool`: 获取所有日程
- `get_schedule_tool`: 获取指定日程
- `update_schedule_tool`: 更新日程
- `delete_schedule_tool`: 删除指定日程
- `get_schedules_by_date_range_tool`: 获取指定日期范围内的日程
- `get_upcoming_schedules_tool`: 获取即将到来的日程
- `refresh_schedule_list_tool`: 刷新前端日程列表

### 笔记管理工具
- `create_note_tool`: 创建新笔记
- `get_notes_tool`: 获取所有笔记
- `get_note_tool`: 获取指定笔记
- `update_note_tool`: 更新笔记
- `delete_note_tool`: 删除指定笔记
- `search_notes_tool`: 搜索笔记
- `get_pinned_notes_tool`: 获取置顶笔记
- `get_recent_notes_tool`: 获取最近笔记
- `refresh_note_list_tool`: 刷新前端笔记列表

## 使用示例

### Agent 初始化

```python
from ..agents import TaskAgent
from ..services import TaskService

task_service = TaskService()
agent = TaskAgent(task_service)
agent.set_user_id(user_id=1)
```

### 工具调用流程

1. Agent 接收用户消息
2. LLM 分析消息并选择合适的工具
3. 工具执行（通过 ResourceToolsManager 路由到对应的工具类）
4. 返回结果给 Agent
5. Agent 生成响应

## 架构优势

1. **模块化设计**: 每类资源有独立的工具类和服务，便于维护和扩展
2. **统一管理**: ResourceToolsManager 提供统一的接口，简化 Agent 的使用
3. **向后兼容**: 保持对原有 TaskTools 的兼容，不影响现有功能
4. **易于扩展**: 未来可以轻松添加新的资源类型（如提醒、标签等）
5. **清晰的职责分离**: 同步服务层、工具层、管理器层各司其职

## 文件结构

```
backend/src/
├── agents/
│   ├── agent.py                    # Agent Graph 定义
│   ├── agent_wrapper.py            # Agent 包装类
│   ├── task_tools.py               # TaskTools（任务工具）
│   ├── schedule_tools.py           # ScheduleTools（日程工具）
│   ├── note_tools.py               # NoteTools（笔记工具）
│   ├── resource_tools_manager.py   # 统一工具管理器
│   ├── prompt.py                   # 系统提示词
│   └── state.py                    # Agent 状态定义
├── services/
│   ├── sync_task_service.py        # 同步任务服务
│   ├── sync_schedule_service.py    # 同步日程服务（新增）
│   └── sync_note_service.py        # 同步笔记服务（新增）
```

## 后续优化建议

1. **工具权限控制**: 可以为不同用户设置不同的工具访问权限
2. **工具调用日志**: 记录所有工具调用，便于调试和审计
3. **批量操作工具**: 添加批量创建、更新、删除的工具
4. **资源关联工具**: 支持任务、日程、笔记之间的关联操作
5. **智能推荐**: 基于用户历史行为推荐相关操作

## 总结

新的 Agent 架构成功地将单一资源类型（任务）扩展为多资源类型（任务、日程、笔记），同时保持了代码的模块化和可维护性。通过统一工具管理器，Agent 可以无缝地管理三类资源，为用户提供更全面的智能助手服务。

