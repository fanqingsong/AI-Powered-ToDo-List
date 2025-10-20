# 动态系统提示词优化

## 问题描述

在AI助手的实现中，系统提示词（system prompt）中的工具描述是硬编码的，这导致以下问题：

1. **工具描述不准确**：硬编码的工具描述可能与实际可用的工具不匹配
2. **维护困难**：每次添加或修改工具时，都需要手动更新系统提示词
3. **功能缺失**：AI助手无法正确识别和使用新添加的工具
4. **用户体验差**：AI助手会报告"任务未找到"等错误，即使任务确实存在

## 解决方案

### 1. 创建动态系统提示词生成函数

在 `backend/src/agents/prompt.py` 中添加了 `generate_dynamic_system_prompt()` 函数：

```python
def generate_dynamic_system_prompt(
    task_tools: Optional[Any] = None,
    frontend_tools_config: Optional[List[Dict[str, Any]]] = None
) -> str:
    """动态生成系统提示词
    
    Args:
        task_tools: 任务工具实例，用于获取工具定义
        frontend_tools_config: 前端工具配置列表
        
    Returns:
        动态生成的系统提示词
    """
```

### 2. 工具描述动态生成

- **后端工具**：从 `TaskTools.get_tool_definitions()` 获取实际工具定义
- **前端工具**：从 `frontend_tools_config` 参数获取配置
- **格式化**：自动移除工具名称的下划线前缀，生成用户友好的描述

### 3. 集成到Agent工作流

在 `backend/src/agents/agent_wrapper.py` 中：

```python
# 动态生成系统提示词
dynamic_system_prompt = generate_dynamic_system_prompt(
    task_tools=self.task_tools,
    frontend_tools_config=frontend_tools_config
)

# 使用动态生成的提示词
messages = [
    {"type": "system", "content": dynamic_system_prompt}
]
```

## 技术实现细节

### 1. 工具定义获取

```python
if task_tools:
    # 获取工具定义
    tool_definitions = task_tools.get_tool_definitions()
    
    # 构建工具描述
    tool_descriptions = []
    for i, tool_def in enumerate(tool_definitions, 1):
        tool_name = tool_def["function"]["name"]
        tool_desc = tool_def["function"]["description"]
        
        # 格式化工具描述
        if tool_name.startswith("_"):
            display_name = tool_name[1:]  # 移除下划线前缀
        else:
            display_name = tool_name
            
        tool_descriptions.append(f"{i}. {display_name} - {tool_desc}")
```

### 2. 前端工具集成

```python
if frontend_tools_config:
    frontend_tools_desc = []
    start_index = len(tool_definitions) + 1 if task_tools else 10
    
    for i, tool_config in enumerate(frontend_tools_config, start_index):
        tool_name = tool_config.get("name", f"frontend_tool_{i}")
        tool_desc = tool_config.get("description", "前端工具")
        frontend_tools_desc.append(f"{i}. {tool_name} - {tool_desc}")
    
    if frontend_tools_desc:
        tools_description += "\n" + "\n".join(frontend_tools_desc)
```

### 3. 向后兼容

保留了原有的 `SYSTEM_PROMPT` 常量，确保现有代码的兼容性：

```python
# 默认系统提示词（向后兼容）
SYSTEM_PROMPT = BASE_SYSTEM_PROMPT_TEMPLATE.format(
    tools_description="""1. create_task_tool - 创建新任务
2. get_tasks_tool - 获取所有任务列表
..."""
)
```

## 测试验证

创建了测试脚本 `cursortest/test_simple_prompt.py` 验证功能：

1. **基础模板测试**：验证工具描述动态生成
2. **前端工具测试**：验证前端工具集成
3. **格式化测试**：验证工具名称格式化

测试结果：
```
✅ 所有测试完成！
```

## 预期效果

### 1. 解决AI助手工具识别问题

- **之前**：AI助手报告"任务'小消息'未找到"，即使任务确实存在
- **之后**：AI助手能正确识别和使用所有可用工具

### 2. 提高维护效率

- **之前**：每次添加工具都需要手动更新系统提示词
- **之后**：工具描述自动同步，无需手动维护

### 3. 增强功能扩展性

- **之前**：硬编码限制工具数量
- **之后**：支持动态添加任意数量的工具

### 4. 改善用户体验

- **之前**：用户遇到"无法执行"错误
- **之后**：AI助手能正确执行用户请求

## 文件变更

1. **backend/src/agents/prompt.py**
   - 添加 `generate_dynamic_system_prompt()` 函数
   - 重构为模板化设计
   - 保持向后兼容

2. **backend/src/agents/agent_wrapper.py**
   - 导入动态提示词生成函数
   - 在消息处理中使用动态提示词
   - 更新配置传递

3. **cursortest/test_simple_prompt.py**
   - 创建测试脚本验证功能
   - 测试基础模板和前端工具集成

## 总结

通过实现动态系统提示词生成，解决了AI助手工具识别不准确的问题，提高了系统的可维护性和扩展性。这个改进确保了AI助手能够正确识别和使用所有可用工具，为用户提供更好的服务体验。
