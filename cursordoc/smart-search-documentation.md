# 智能搜索功能文档

## 概述

智能搜索功能是基于向量数据库（Weaviate）的语义搜索系统，能够理解用户查询的语义含义，而不仅仅是关键词匹配。该功能为笔记管理提供了强大的搜索能力。

## 功能特性

### 1. 语义搜索
- 支持自然语言查询
- 理解查询意图和上下文
- 返回语义相关的笔记内容

### 2. 即时同步
- 笔记创建/更新时自动同步到向量数据库
- 删除笔记时自动从向量数据库移除
- 确保搜索结果的实时性

### 3. 定时同步
- 每小时自动同步所有用户笔记
- 每天凌晨清理过期数据
- 保证数据一致性

### 4. 高级过滤
- 按分类过滤搜索结果
- 按标签过滤搜索结果
- 支持包含/排除归档笔记

### 5. 搜索建议
- 基于用户笔记内容生成搜索建议
- 智能推荐相关搜索词
- 提高搜索效率

## 技术架构

### 后端组件

1. **Weaviate 客户端** (`services/weaviate_client.py`)
   - 管理向量数据库连接
   - 处理笔记的增删改查
   - 执行向量搜索

2. **智能搜索服务** (`services/smart_search_service.py`)
   - 提供搜索接口
   - 处理搜索逻辑
   - 生成搜索建议

3. **笔记同步服务** (`services/note_sync_service.py`)
   - 处理笔记同步逻辑
   - 管理同步状态

4. **Celery 任务** (`tasks/`)
   - 异步处理同步任务
   - 定时执行批量同步
   - 清理过期数据

5. **API 路由** (`routes/smart_search.py`)
   - 提供 RESTful API
   - 处理前端请求
   - 返回搜索结果

### 前端组件

1. **智能搜索API** (`services/smartSearchApi.ts`)
   - 封装搜索相关API调用
   - 处理请求和响应

2. **智能搜索组件** (`components/SmartSearch.tsx`)
   - 提供搜索界面
   - 显示搜索结果
   - 管理搜索状态

3. **笔记管理器集成**
   - 在笔记管理页面添加智能搜索标签页
   - 提供统一的用户体验

## 部署配置

### 环境变量

```bash
# Weaviate 配置
WEAVIATE_HOST=localhost
WEAVIATE_PORT=8080
WEAVIATE_SCHEME=http

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key_here
```

### Docker 服务

```yaml
# docker-compose.yml 中的相关服务
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  weaviate:
    image: semitechnologies/weaviate:1.22.4
    ports:
      - "8080:8080"
    environment:
      - DEFAULT_VECTORIZER_MODULE=none
      - ENABLE_MODULES=text2vec-openai
  
  celery-worker:
    command: celery -A src.celery_app worker --loglevel=info
  
  celery-beat:
    command: celery -A src.celery_app beat --loglevel=info
```

## 使用方法

### 1. 基本搜索

在前端笔记管理页面，切换到"智能搜索"标签页：

1. 在搜索框中输入查询内容
2. 选择搜索参数（结果数量、分类、是否包含归档）
3. 点击搜索或按回车键
4. 查看搜索结果

### 2. 高级搜索

- **分类过滤**: 选择特定分类进行搜索
- **标签过滤**: 输入标签进行过滤
- **归档包含**: 选择是否包含已归档的笔记
- **结果数量**: 设置返回结果的最大数量

### 3. 搜索建议

- 输入搜索内容时会自动显示建议
- 点击建议可以快速搜索
- 建议基于用户的历史笔记内容生成

### 4. 相似笔记

- 在笔记详情页面可以查看相似笔记
- 基于笔记内容的语义相似性推荐

## API 接口

### 智能搜索

```http
POST /api/smart-search/smart-search
Content-Type: application/json
Authorization: Bearer <token>

{
  "query": "搜索内容",
  "limit": 10,
  "category": "PERSONAL",
  "tags": ["标签1", "标签2"],
  "include_archived": false
}
```

### 获取相似笔记

```http
POST /api/smart-search/similar-notes
Content-Type: application/json
Authorization: Bearer <token>

{
  "note_id": 123,
  "limit": 5
}
```

### 获取搜索建议

```http
POST /api/smart-search/search-suggestions
Content-Type: application/json
Authorization: Bearer <token>

{
  "query": "搜索内容",
  "limit": 5
}
```

### 搜索统计

```http
GET /api/smart-search/search-stats
Authorization: Bearer <token>
```

### 重新索引

```http
POST /api/smart-search/reindex
Authorization: Bearer <token>
```

## 监控和维护

### 1. 健康检查

```http
GET /api/smart-search/health
```

返回搜索服务的健康状态。

### 2. 日志监控

```bash
# 查看 Celery Worker 日志
docker-compose logs -f celery-worker

# 查看 Celery Beat 日志
docker-compose logs -f celery-beat

# 查看后端服务日志
docker-compose logs -f backend
```

### 3. 数据同步状态

- 检查 Celery 任务队列状态
- 监控向量数据库中的数据量
- 查看同步任务的执行结果

## 故障排除

### 常见问题

1. **搜索服务不可用**
   - 检查 Weaviate 服务是否正常运行
   - 验证 OPENAI_API_KEY 是否正确配置
   - 查看后端服务日志

2. **搜索结果不准确**
   - 检查笔记是否已同步到向量数据库
   - 尝试重新索引用户笔记
   - 验证向量化模型是否正常工作

3. **同步任务失败**
   - 检查 Celery Worker 是否正常运行
   - 验证数据库连接是否正常
   - 查看任务执行日志

### 调试命令

```bash
# 检查服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f <service_name>

# 重启服务
docker-compose restart <service_name>

# 进入容器调试
docker-compose exec backend bash
```

## 性能优化

### 1. 向量数据库优化
- 定期清理过期数据
- 优化向量索引
- 调整搜索参数

### 2. 缓存策略
- 缓存热门搜索结果
- 使用 Redis 缓存搜索建议
- 实现搜索结果分页

### 3. 异步处理
- 使用 Celery 异步处理同步任务
- 实现批量同步优化
- 添加任务优先级

## 安全考虑

### 1. 数据隔离
- 确保用户只能搜索自己的笔记
- 实现严格的权限控制
- 防止数据泄露

### 2. API 安全
- 使用 JWT 认证
- 实现请求频率限制
- 添加输入验证

### 3. 数据保护
- 加密敏感数据
- 实现数据备份
- 添加审计日志

## 未来扩展

### 1. 功能增强
- 支持多语言搜索
- 添加搜索历史
- 实现个性化推荐

### 2. 性能提升
- 使用更先进的向量模型
- 实现分布式搜索
- 添加实时搜索

### 3. 用户体验
- 添加搜索高亮
- 实现搜索预览
- 提供搜索分析
