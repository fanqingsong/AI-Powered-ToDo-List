# Agent Graph Builder 架构文档

## 概述

`agent.py` 模块专门负责构建和管理 LangGraph 工作流，将图构建逻辑从主要的 Agent 类中分离出来，提高了代码的可维护性和可扩展性。

## 架构设计

### 核心组件

1. **AgentGraphBuilder 类**
   - 主要的图构建器类
   - 负责创建不同类型的 LangGraph 工作流
   - 支持自定义节点和边的配置

2. **FrontendTool 类**
   - 专门处理前端工具调用的工具类
   - 继承自 LangChain 的 BaseTool
   - 通过抛出 NodeInterrupt 异常来处理前端工具调用

3. **AnyArgsSchema 类**
   - 允许任意参数的 Pydantic Schema
   - 用于前端工具的灵活参数处理

### 图类型

#### 1. Agent 图 (`build`)
- 专门为 Assistant-UI 组件设计
- 支持前端工具调用
- 包含完整的工具定义和实例管理

#### 2. 标准图 (`build_standard_graph`)
- 标准的任务管理工作流
- 不包含前端工具
- 适用于后端 API 调用

#### 3. 自定义图 (`build_custom_graph`)
- 支持自定义节点和边的配置
- 提供最大的灵活性
- 适用于特殊业务需求

## 使用方式

### 基本使用

```python
from src.agents.agent import create_agent_builder
from src.agents.tools import TaskTools
from src.agents.llmconf import get_llm

# 初始化依赖
llm = get_llm()
task_tools = TaskTools(task_service)

# 创建图构建器
graph_builder = create_agent_builder(llm, task_tools)

# 构建不同类型的图
agent = graph_builder.build()
standard_graph = graph_builder.build_standard_graph()
```

### 自定义图使用

```python
# 定义自定义节点
def custom_node(state, config):
    return {"messages": "custom processing"}

# 构建自定义图
custom_graph = graph_builder.build_custom_graph(
    custom_nodes={"custom": custom_node},
    custom_edges=[("agent", "custom"), ("custom", END)],
    entry_point="agent"
)
```

## 工作流结构

### 标准工作流
```
agent -> [should_continue] -> tools -> agent
         |                    |
         v                    v
        END                  END
```

### Assistant-UI 工作流
```
agent -> [should_continue] -> tools -> agent
         |                    |
         v                    v
        END                  END
```
- 支持前端工具调用
- 包含完整的工具定义管理

## 配置参数

### 图配置
- `custom_nodes`: 自定义节点字典
- `custom_edges`: 自定义边列表
- `entry_point`: 入口节点名称

### 工具配置
- `frontend_tools`: 前端工具配置列表
- `system`: 系统提示词
- `thread_id`: 会话线程ID

## 错误处理

### NodeInterrupt 异常
- 用于处理前端工具调用
- 允许工作流中断并返回前端处理

### 工具调用错误
- 自动处理工具执行失败
- 提供详细的错误信息

## 扩展性

### 添加新节点类型
1. 在 `AgentGraphBuilder` 中添加新的构建方法
2. 定义节点函数
3. 配置节点间的连接关系

### 添加新工具类型
1. 继承 `BaseTool` 类
2. 实现 `_run` 和 `_arun` 方法
3. 在工具管理器中注册

## 性能优化

### 图编译
- 所有图在创建时进行编译
- 避免运行时的重复编译开销

### 工具绑定
- 工具在模型调用时动态绑定
- 支持运行时工具配置更新

## 测试

运行测试脚本：
```bash
python cursortest/test_agent.py
```

测试覆盖：
- 图构建器创建
- 不同类型图的构建
- 自定义图配置
- 错误处理

## 迁移指南

### 从旧版本迁移
1. 更新导入语句：
   ```python
   from src.agents.agent import create_agent_builder
   ```

2. 替换图构建逻辑：
   ```python
   # 旧方式
   self.agent = self._build_agent()
   
   # 新方式
   self.graph_builder = create_agent_builder(self.llm, self.task_tools)
   self.agent = self.graph_builder.build()
   ```

3. 移除旧的图构建方法

## 最佳实践

1. **单一职责**: 每个图构建方法只负责一种特定类型的工作流
2. **配置分离**: 将配置参数与图构建逻辑分离
3. **错误处理**: 提供详细的错误信息和恢复机制
4. **文档完整**: 为每个方法提供详细的文档字符串
5. **测试覆盖**: 确保所有功能都有对应的测试用例
