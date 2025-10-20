# 前端工具集成使用说明

## 概述

本项目实现了基于 `@assistant-ui/react` 的前端工具集成机制，允许 AI 助手调用前端工具来执行各种操作，如刷新任务列表、页面导航、显示通知等。

## 架构设计

### 后端工具集成

1. **FrontendTool 基类** (`backend/src/agents/tools.py`)
   - 定义了前端工具的基类
   - 使用 `NodeInterrupt` 机制来处理前端工具调用
   - 支持任意参数模式 (`AnyArgsSchema`)

2. **TaskTools 类增强**
   - 支持前端工具配置
   - 提供工具定义和工具实例的分离
   - 动态配置前端工具

3. **Agent 配置更新** (`backend/src/agents/agent_wrapper.py`)
   - 支持前端工具配置参数
   - 处理前端工具中断
   - 流式响应中包含前端工具调用信息

### 前端工具实现

1. **AssistantUIWithTools 组件** (`frontend/src/components/AssistantUIWithTools.tsx`)
   - 基于 `@assistant-ui/react` 实现
   - 监听助手消息中的工具调用指令
   - 支持多种前端工具类型

2. **工具类型支持**
   - `refresh_task_list`: 刷新任务列表
   - `navigate_to_page`: 页面导航
   - `show_notification`: 显示通知
   - `open_modal`: 打开模态框
   - `update_ui_state`: 更新UI状态

## 使用方法

### 1. 后端配置

在调用聊天 API 时，可以传递前端工具配置：

```typescript
const chatRequest = {
  message: "刷新任务列表",
  sessionId: "session_123",
  userId: "user_456",
  frontend_tools_config: [
    {
      name: "refresh_task_list",
      description: "刷新前端任务列表，获取最新的任务数据"
    },
    {
      name: "navigate_to_page",
      description: "导航到指定页面"
    }
  ]
};
```

### 2. 前端集成

在组件中使用 `AssistantUIWithTools`：

```tsx
import AssistantUIWithTools from './components/AssistantUIWithTools';

function MyComponent() {
  const handleRefreshTaskList = () => {
    // 刷新任务列表的逻辑
    setTaskRefreshTrigger(prev => prev + 1);
  };

  const handlePageNavigate = (pageKey: string) => {
    // 页面导航的逻辑
    setSelectedMenuKey(pageKey);
  };

  return (
    <AssistantUIWithTools
      onRefreshTaskList={handleRefreshTaskList}
      onPageNavigate={handlePageNavigate}
    />
  );
}
```

### 3. 工具调用方式

AI 助手可以通过以下方式调用前端工具：

1. **直接指令**：在消息中包含特定指令
   - `刷新任务列表` → 触发 `refresh_task_list` 工具
   - `打开系统设置` → 触发 `navigate_to_page` 工具

2. **工具调用标识**：通过特殊标识符
   - `frontend_tool_call:refresh_task_list` → 直接调用刷新工具
   - `frontend_refresh_task_list` → 触发任务列表刷新

## 工具类型详解

### refresh_task_list
- **功能**：刷新前端任务列表
- **触发方式**：消息包含"刷新任务列表"或"frontend_refresh_task_list"
- **效果**：更新任务列表显示，显示成功通知

### navigate_to_page
- **功能**：导航到指定页面
- **参数**：page_key (settings, tasks, calendar, notes, analytics)
- **触发方式**：消息包含"打开[页面名]"或"navigate_to_[page_key]"
- **效果**：切换到指定页面，显示导航通知

### show_notification
- **功能**：显示通知消息
- **触发方式**：消息包含"frontend_tool_call:show_notification"
- **效果**：显示信息通知

### open_modal
- **功能**：打开模态框
- **触发方式**：消息包含"frontend_tool_call:open_modal"
- **效果**：显示模态框打开通知

### update_ui_state
- **功能**：更新UI状态
- **触发方式**：消息包含"frontend_tool_call:update_ui_state"
- **效果**：显示UI状态更新通知

## 扩展指南

### 添加新的前端工具

1. **后端配置**
   ```python
   # 在 tools.py 中添加新的前端工具配置
   default_frontend_tools = [
       {
           "name": "your_new_tool",
           "description": "你的新工具描述"
       }
   ]
   ```

2. **前端处理**
   ```tsx
   // 在 AssistantUIWithTools.tsx 中添加处理逻辑
   switch (toolName) {
     case 'your_new_tool':
       // 执行新工具的逻辑
       break;
   }
   ```

3. **API 调用**
   ```typescript
   // 在聊天请求中包含新工具配置
   frontend_tools_config: [
     {
       name: "your_new_tool",
       description: "你的新工具描述"
     }
   ]
   ```

### 自定义工具参数

前端工具支持任意参数，可以通过以下方式传递：

```typescript
// 后端工具调用
{
  "tool_name": "custom_tool",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

```tsx
// 前端处理
const handleCustomTool = (params: any) => {
  console.log('工具参数:', params);
  // 处理参数
};
```

## 测试

使用提供的测试脚本验证功能：

```bash
python cursortest/test_frontend_tools_integration.py
```

测试脚本会：
1. 检查后端服务健康状态
2. 测试前端工具配置
3. 验证各种工具调用功能
4. 检查流式响应处理

## 注意事项

1. **工具调用顺序**：前端工具调用会中断后端流程，确保前端处理完成后继续
2. **错误处理**：所有工具调用都包含错误处理机制
3. **性能考虑**：避免频繁的工具调用，合理使用防抖机制
4. **安全性**：前端工具调用需要适当的权限验证

## 故障排除

### 常见问题

1. **工具调用不生效**
   - 检查前端工具配置是否正确传递
   - 确认消息内容包含正确的触发指令
   - 查看浏览器控制台是否有错误

2. **页面导航失败**
   - 确认 `onPageNavigate` 回调函数已正确传递
   - 检查页面标识符是否正确

3. **任务列表不刷新**
   - 确认 `onRefreshTaskList` 回调函数已正确传递
   - 检查任务列表组件的刷新机制

### 调试技巧

1. **查看控制台日志**：所有工具调用都会在控制台输出日志
2. **检查网络请求**：查看 API 请求是否包含前端工具配置
3. **验证消息内容**：确认 AI 助手的响应包含正确的工具调用指令

## 更新日志

- **v1.0.0**: 初始实现，支持基本的前端工具集成
- **v1.1.0**: 添加了更多工具类型和错误处理
- **v1.2.0**: 优化了工具调用机制和用户体验
