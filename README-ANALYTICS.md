# AI Native 智能工作台 - 数据分析功能

## 功能概述

数据分析功能为 AI Native 智能工作台提供了全面的数据统计和可视化分析，帮助用户了解工作习惯、提高生产力。

## 主要功能

### 📊 任务分析
- **完成率统计**：显示任务完成率趋势
- **时间分析**：平均完成时间统计
- **趋势图表**：按天/周/月显示任务完成情况

### 📝 笔记分析
- **分类统计**：笔记分类分布饼图
- **字数统计**：总字数、平均字数分析
- **标签分析**：最常用标签统计
- **置顶/归档**：笔记管理状态统计

### 📅 日程分析
- **优先级分布**：日程优先级柱状图
- **完成率统计**：日程完成情况分析
- **时长分析**：平均日程持续时间

### 👥 用户活动分析
- **活跃用户**：系统用户活跃度统计
- **新用户趋势**：用户增长趋势图
- **活动分布**：按时间段统计用户活动

### 🏆 生产力指标
- **生产力评分**：综合评分系统 (0-100)
- **连续活跃天数**：用户连续使用天数
- **工作时长**：每日工作时长统计
- **目标进度**：周目标完成进度

## 技术实现

### 后端技术栈
- **FastAPI**：高性能 Web 框架
- **SQLAlchemy**：ORM 数据库操作
- **PostgreSQL**：关系型数据库
- **Pydantic**：数据验证和序列化

### 前端技术栈
- **React 18**：用户界面框架
- **TypeScript**：类型安全的 JavaScript
- **Ant Design**：企业级 UI 组件库
- **Recharts**：数据可视化图表库

### 图表类型
- **折线图**：趋势分析
- **饼图**：分类占比
- **柱状图**：对比分析
- **面积图**：累积数据

## API 端点

### 分析概览
```
GET /api/analytics/overview?time_range=month&include_charts=true
```

### 任务分析
```
GET /api/analytics/tasks?time_range=month
```

### 笔记分析
```
GET /api/analytics/notes?time_range=month
```

### 日程分析
```
GET /api/analytics/schedules?time_range=month
```

### 生产力指标
```
GET /api/analytics/productivity
```

### 图表数据
```
GET /api/analytics/charts?time_range=month&chart_type=line
```

## 时间范围选项

- `today` - 今日
- `week` - 本周
- `month` - 本月
- `quarter` - 本季度
- `year` - 本年
- `all` - 全部

## 启动服务

### 使用脚本启动
```bash
# 启动所有服务
./start-services.sh

# 停止所有服务
./stop-services.sh
```

### 手动启动
```bash
# 创建网络
docker network create ai-todo-network

# 启动数据库
docker run -d --name ai-todo-postgres \
  --network ai-todo-network \
  -p 5432:5432 \
  -e POSTGRES_DB=ai_todo_db \
  -e POSTGRES_USER=ai_todo_user \
  -e POSTGRES_PASSWORD=ai_todo_password \
  postgres:15-alpine

# 启动后端
docker run -d --name ai-todo-backend \
  --network ai-todo-network \
  -p 3000:3000 \
  -e DATABASE_URL=postgresql://ai_todo_user:ai_todo_password@ai-todo-postgres:5432/ai_todo_db \
  ai-powered-todo-list_backend

# 启动前端
docker run -d --name ai-todo-frontend \
  --network ai-todo-network \
  -p 3001:3000 \
  ai-powered-todo-list_frontend
```

## 访问地址

- **前端应用**：http://localhost:3001
- **后端API**：http://localhost:3000
- **API文档**：http://localhost:3000/docs

## 使用说明

1. 访问前端应用
2. 登录系统（默认管理员账号：admin/password）
3. 在左侧菜单中点击"数据分析"
4. 选择时间范围查看不同时期的数据
5. 浏览各种图表和统计信息

## 数据说明

### 测试数据
系统已预置测试数据，包括：
- 用户：admin（管理员）、testuser（普通用户）
- 任务：已完成和待完成的任务
- 笔记：不同分类的笔记记录
- 日程：不同优先级的日程安排

### 数据更新
- 数据实时更新
- 支持多用户数据隔离
- 自动计算统计指标

## 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   # 检查容器状态
   docker ps -a
   
   # 查看容器日志
   docker logs ai-todo-backend
   docker logs ai-todo-frontend
   docker logs ai-todo-postgres
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库状态
   docker exec ai-todo-postgres psql -U ai_todo_user -d ai_todo_db -c "\dt"
   ```

3. **前端无法访问**
   ```bash
   # 检查端口占用
   netstat -tlnp | grep :3001
   ```

### 重置服务
```bash
# 停止所有服务
./stop-services.sh

# 重新启动
./start-services.sh
```

## 开发说明

### 添加新的分析指标
1. 在 `backend/src/models/analytics.py` 中定义数据模型
2. 在 `backend/src/services/analytics_service.py` 中实现计算逻辑
3. 在 `backend/src/routes/analytics.py` 中添加 API 端点
4. 在 `frontend/src/services/analyticsApi.ts` 中添加 API 调用
5. 在 `frontend/src/components/AnalyticsManager.tsx` 中添加 UI 组件

### 添加新的图表类型
1. 在 `backend/src/models/analytics.py` 中定义图表类型
2. 在 `backend/src/services/analytics_service.py` 中生成图表数据
3. 在 `frontend/src/components/AnalyticsManager.tsx` 中添加图表组件

## 许可证

本项目采用 MIT 许可证。
