# LangGraph Agent 使用指南

本项目已成功从 Azure Foundry Agent 迁移到基于 LangGraph 的 agent 实现，支持多种 LLM 提供商。

## 🚀 主要特性

### 支持的 LLM 提供商
1. **Azure OpenAI**（推荐）
2. **标准 OpenAI**
3. **Anthropic Claude**
4. **降级模式**（无 API Key 时）

### 核心功能
- ✅ **任务管理**：创建、查看、更新、删除任务
- ✅ **智能对话**：基于 LangGraph 的 AI 助手
- ✅ **工具调用**：自动调用任务管理工具
- ✅ **多语言支持**：中文界面和回复

## 🔧 配置说明

### 1. Azure OpenAI 配置（推荐）

在 `.env` 文件中配置：

```bash
# Azure OpenAI 配置
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 2. 标准 OpenAI 配置

```bash
# 标准 OpenAI API
OPENAI_API_KEY=your_openai_api_key
```

### 3. Anthropic 配置

```bash
# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## 🎯 使用方法

### 启动应用

```bash
# 使用启动脚本
./start.sh

# 或手动启动
docker compose up --build -d
```

### 访问应用

- **应用地址**：http://localhost:3000
- **API 文档**：http://localhost:3000/docs
- **健康检查**：http://localhost:3000/api/health

### 聊天功能

发送 POST 请求到 `/api/chat/foundry`：

```bash
curl -X POST http://localhost:3000/api/chat/foundry \
  -H "Content-Type: application/json" \
  -d '{"message": "请帮我创建一个新任务：学习 LangGraph"}'
```

### 任务管理 API

```bash
# 获取所有任务
curl http://localhost:3000/api/tasks

# 创建任务
curl -X POST http://localhost:3000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "新任务", "isComplete": false}'

# 更新任务
curl -X PUT http://localhost:3000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "更新的任务", "isComplete": true}'

# 删除任务
curl -X DELETE http://localhost:3000/api/tasks/1
```

## 🤖 AI 助手功能

### 支持的自然语言指令

- **创建任务**：
  - "请帮我创建一个新任务：学习 Python"
  - "添加一个任务：完成项目文档"

- **查看任务**：
  - "显示所有任务"
  - "查看我的任务列表"
  - "任务 1 的详情是什么？"

- **更新任务**：
  - "将任务 1 标记为完成"
  - "修改任务 2 的标题为：学习 LangGraph"

- **删除任务**：
  - "删除任务 1"
  - "移除已完成的任务"

### 示例对话

```
用户：你好，请帮我创建一个新任务：学习 LangGraph
助手：好的，我已经为您创建了一个新任务："学习 LangGraph" (ID: 1)

用户：显示所有任务
助手：找到 1 个任务:
- 1: 学习 LangGraph (未完成)

用户：将任务 1 标记为完成
助手：任务 1 更新成功。

用户：查看任务 1 的详情
助手：任务 1: "学习 LangGraph" - 状态: 已完成
```

## 🔄 降级模式

当没有配置任何 API Key 时，应用会自动进入降级模式：

- ✅ **任务管理功能**：完全可用
- ⚠️ **AI 聊天功能**：显示配置提示

降级模式下的聊天回复：
```
抱歉，AI 功能当前不可用。请配置以下任一环境变量以启用 AI 功能：

• Azure OpenAI: AZURE_OPENAI_API_KEY 和 AZURE_OPENAI_ENDPOINT
• 标准 OpenAI: OPENAI_API_KEY
• Anthropic: ANTHROPIC_API_KEY

您仍然可以使用以下功能：
- 查看任务列表
- 创建新任务
- 更新任务状态
- 删除任务
```

## 🛠️ 技术架构

### LangGraph 工作流

```
用户消息 → 系统提示 → LLM 处理 → 工具调用 → 任务操作 → 结果返回
```

### 工具定义

- `create_task`: 创建新任务
- `get_tasks`: 获取所有任务
- `get_task`: 获取特定任务
- `update_task`: 更新任务
- `delete_task`: 删除任务

### 状态管理

使用 LangGraph 的 `StateGraph` 管理对话状态和工具调用流程。

## 📊 性能优化

### 镜像加速
- **Docker Hub**: 华为云镜像加速
- **APT 包管理**: 阿里云镜像源
- **Python pip**: 清华大学镜像源

### 构建优化
- 多阶段构建（可选）
- `.dockerignore` 优化
- 依赖版本兼容性

## 🔍 故障排除

### 常见问题

1. **连接错误**
   - 检查 API Key 是否正确
   - 验证网络连接
   - 确认端点 URL 格式

2. **工具调用失败**
   - 查看应用日志
   - 检查数据库连接
   - 验证任务服务状态

3. **降级模式**
   - 配置正确的环境变量
   - 重启应用容器

### 调试命令

```bash
# 查看容器状态
docker compose ps

# 查看应用日志
docker compose logs -f

# 进入容器调试
docker compose exec todo-app bash

# 测试健康检查
curl http://localhost:3000/api/health
```

## 🎉 总结

新的 LangGraph agent 实现提供了：

- **更好的灵活性**：支持多种 LLM 提供商
- **更强的可扩展性**：基于 LangGraph 的工作流
- **更简单的部署**：无需复杂的 Azure 配置
- **更好的用户体验**：中文界面和智能对话

现在您可以使用一个命令启动整个项目，并通过自然语言与 AI 助手交互来管理任务！
