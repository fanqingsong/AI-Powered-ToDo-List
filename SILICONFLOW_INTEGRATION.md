# 硅基流动接口集成说明

## 概述

本项目已成功集成硅基流动（SiliconFlow）API接口，支持使用硅基流动提供的多种大语言模型进行AI任务管理。

## 功能特点

- ✅ 支持硅基流动API接口
- ✅ 兼容OpenAI API格式
- ✅ 支持多种模型选择
- ✅ 自动配置优先级管理
- ✅ 环境变量配置支持

## 支持的模型

硅基流动提供多种大语言模型，包括：

- `deepseek-chat` - DeepSeek Chat（默认）
- `qwen2.5-72b-instruct` - Qwen2.5 72B
- `qwen2.5-32b-instruct` - Qwen2.5 32B
- `glm-4-9b-chat` - GLM-4 9B
- `llama-3.1-8b-instruct` - Llama 3.1 8B
- `gemma-2-9b-it` - Gemma 2 9B
- 更多模型请参考[硅基流动官方文档](https://siliconflow.cn)

## 配置方法

### 1. 环境变量配置

在 `.env` 文件中添加以下配置：

```bash
# 硅基流动配置
SILICONFLOW_API_KEY=your_siliconflow_api_key
SILICONFLOW_MODEL=deepseek-chat
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
```

### 2. 系统环境变量

```bash
export SILICONFLOW_API_KEY="your_api_key_here"
export SILICONFLOW_MODEL="deepseek-chat"
export SILICONFLOW_BASE_URL="https://api.siliconflow.cn/v1"
```

### 3. Docker环境

在 `docker-compose.yml` 中添加环境变量：

```yaml
services:
  backend:
    environment:
      - SILICONFLOW_API_KEY=your_api_key_here
      - SILICONFLOW_MODEL=deepseek-chat
      - SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
```

## 配置优先级

系统按以下优先级选择LLM提供商：

1. **Azure OpenAI** (最高优先级)
2. **硅基流动** 
3. **OpenAI**
4. **Anthropic** (最低优先级)

## 使用方法

### 1. 获取API密钥

1. 访问[硅基流动官网](https://siliconflow.cn)
2. 注册账户并登录
3. 在控制台中获取API密钥

### 2. 配置应用

1. 设置 `SILICONFLOW_API_KEY` 环境变量
2. 可选：设置 `SILICONFLOW_MODEL` 选择特定模型
3. 可选：设置 `SILICONFLOW_BASE_URL` 自定义API端点

### 3. 启动应用

```bash
# 开发环境
./start-dev.sh

# 生产环境
docker compose up -d
```

## 代码变更

### 1. LLM配置模块 (`backend/src/agents/llm_config.py`)

- 添加了硅基流动API支持
- 更新了LLM可用性检查逻辑
- 设置了正确的配置优先级

### 2. 环境变量配置 (`backend/env.example`)

- 添加了硅基流动相关配置示例
- 包含完整的配置说明

## 测试验证

系统会自动检测配置并选择可用的LLM提供商。可以通过以下方式验证：

1. 检查应用启动日志
2. 查看LLM配置状态
3. 测试AI任务管理功能

## 故障排除

### 常见问题

1. **API密钥无效**
   - 检查 `SILICONFLOW_API_KEY` 是否正确设置
   - 确认API密钥在硅基流动控制台中有效

2. **模型不可用**
   - 检查 `SILICONFLOW_MODEL` 是否支持
   - 尝试使用默认模型 `deepseek-chat`

3. **网络连接问题**
   - 检查 `SILICONFLOW_BASE_URL` 是否正确
   - 确认网络可以访问 `api.siliconflow.cn`

### 调试方法

1. 查看应用日志
2. 检查环境变量设置
3. 测试API连接

## 成本优势

硅基流动提供高性价比的API服务：

- Qwen2-72B: 4.13元/百万Token
- 9B及以下模型: 永久免费
- 支持多种开源模型

## 技术支持

- [硅基流动官方文档](https://siliconflow.cn)
- [API接口文档](https://siliconflow.cn/docs)
- [社区支持](https://siliconflow.cn/community)

## 更新日志

- **v1.0.0** - 初始集成硅基流动API支持
- 支持多种模型选择
- 自动配置优先级管理
- 环境变量配置支持
