# 自定义嵌入服务使用说明

## 概述

项目已成功改造为支持多种厂商嵌入模型的自定义向量化方案。现在可以灵活选择使用 OpenAI、Cohere 或 Hugging Face 的嵌入模型。

## 主要改动

### 1. 新增文件
- `celery/src/tasks/services/embedding_service.py` - 自定义嵌入服务模块
- `cursortest/test_embedding_service.py` - 测试脚本

### 2. 修改文件
- `docker-compose.yml` - 禁用 Weaviate 自动向量化
- `celery/src/tasks/services/weaviate_client.py` - 支持自定义向量化
- `celery/src/tasks/services/note_sync_service.py` - 使用新的嵌入服务
- `celery/src/tasks/vector_sync_tasks.py` - 更新 Celery 任务
- `celery/requirements.txt` - 添加嵌入模型依赖
- `celery/env.example` - 更新环境变量配置
- `backend/env.example` - 更新环境变量配置

## 配置说明

### 环境变量配置

在 `.env` 文件中配置嵌入服务：

```bash
# 选择嵌入提供商
EMBEDDING_PROVIDER=openai  # 或 cohere, huggingface

# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Cohere 配置
COHERE_API_KEY=your_cohere_api_key
COHERE_EMBEDDING_MODEL=embed-multilingual-v2.0

# Hugging Face 配置
HF_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
HUGGINGFACE_API_KEY=your_huggingface_api_key
```

### 支持的嵌入提供商

#### 1. OpenAI
- **模型**: text-embedding-3-small, text-embedding-3-large
- **维度**: 1536 (small), 3072 (large)
- **优势**: 高质量嵌入，支持多语言
- **成本**: 按 token 计费

#### 2. Cohere
- **模型**: embed-multilingual-v2.0, embed-english-v3.0
- **维度**: 768 (multilingual), 1024 (english)
- **优势**: 多语言支持，成本较低
- **成本**: 按 token 计费

#### 3. Hugging Face
- **模型**: sentence-transformers/all-MiniLM-L6-v2, all-mpnet-base-v2
- **维度**: 384 (MiniLM), 768 (mpnet)
- **优势**: 免费，可离线运行
- **成本**: 免费（本地模型）

## 使用方法

### 1. 启动服务

```bash
# 重新构建并启动服务
docker compose down
docker compose up --build -d
```

### 2. 测试嵌入功能

```bash
# 运行测试脚本
cd /home/song/workspace/me/AI-Powered-ToDo-List
python cursortest/test_embedding_service.py
```

### 3. 切换嵌入提供商

修改 `.env` 文件中的 `EMBEDDING_PROVIDER` 变量：

```bash
# 使用 OpenAI
EMBEDDING_PROVIDER=openai

# 使用 Cohere
EMBEDDING_PROVIDER=cohere

# 使用 Hugging Face
EMBEDDING_PROVIDER=huggingface
```

重启服务即可生效。

## 技术实现

### 1. 嵌入服务架构

```
EmbeddingService
├── OpenAIEmbeddingProvider
├── CohereEmbeddingProvider
└── HuggingFaceEmbeddingProvider
```

### 2. 向量化流程

1. **文本输入** → 嵌入服务
2. **生成向量** → 自定义嵌入模型
3. **存储向量** → Weaviate（禁用自动向量化）
4. **搜索查询** → 生成查询向量 → 向量相似度搜索

### 3. 错误处理

- 嵌入服务失败时回退到文本搜索
- 支持部分失败（部分笔记有向量，部分没有）
- 详细的错误日志记录

## 性能优化

### 1. 批量处理
- 支持批量文本嵌入
- 减少 API 调用次数

### 2. 缓存策略
- 可以考虑添加向量缓存
- 避免重复计算相同文本的向量

### 3. 异步处理
- Celery 任务异步处理向量化
- 不阻塞主业务流程

## 监控和调试

### 1. 日志查看
```bash
# 查看 Celery 日志
docker logs ai-todo-celery-worker

# 查看 Weaviate 日志
docker logs ai-todo-weaviate
```

### 2. 测试命令
```bash
# 测试嵌入服务
python cursortest/test_embedding_service.py

# 测试向量搜索
curl -X POST http://localhost:3000/api/notes/search \
  -H "Content-Type: application/json" \
  -d '{"query": "测试搜索", "user_id": 1}'
```

## 故障排除

### 1. 常见问题

**问题**: 嵌入服务创建失败
**解决**: 检查 API Key 配置和环境变量

**问题**: 向量维度不匹配
**解决**: 确保使用相同模型生成和搜索向量

**问题**: Weaviate 连接失败
**解决**: 检查 Weaviate 服务状态和网络连接

### 2. 调试步骤

1. 检查环境变量配置
2. 验证 API Key 有效性
3. 测试嵌入服务连接
4. 检查 Weaviate 服务状态
5. 查看详细错误日志

## 扩展功能

### 1. 添加新的嵌入提供商

1. 继承 `EmbeddingProvider` 基类
2. 实现 `embed_text` 和 `embed_texts` 方法
3. 在 `create_embedding_service` 中添加新提供商
4. 更新环境变量配置

### 2. 自定义模型

1. 使用 Hugging Face 本地模型
2. 训练自定义嵌入模型
3. 集成企业级嵌入服务

## 总结

通过这次改造，项目现在支持：

✅ **多厂商嵌入模型支持** - OpenAI、Cohere、Hugging Face
✅ **灵活的配置管理** - 通过环境变量切换提供商
✅ **自定义向量化** - 完全控制向量生成过程
✅ **错误处理和回退** - 嵌入失败时回退到文本搜索
✅ **性能优化** - 批量处理和异步任务
✅ **易于扩展** - 模块化设计，易于添加新提供商

这个方案提供了最大的灵活性，可以根据需求、成本和性能要求选择最适合的嵌入模型。
