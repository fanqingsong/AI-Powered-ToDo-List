# AI 智能任务管理器

基于 LangGraph 和 React 的智能任务管理应用，支持传统手动管理和 AI 对话式管理两种方式。

![Task Management AI Agent](ai-powered-todo-list-min.gif)

## ✨ 功能特性

- **🎯 双重管理方式**：支持传统手动管理和 AI 对话式管理
- **🤖 AI 智能助手**：基于 LangGraph 的智能对话系统
- **🎨 现代化 UI**：使用 Ant Design 构建的优美界面
- **📱 响应式设计**：支持桌面和移动设备
- **🐳 容器化部署**：Docker Compose 一键启动
- **🌐 前后端分离**：React 前端 + FastAPI 后端

## 🚀 快速开始

### 一键启动（推荐）

```bash
./start-fullstack.sh
```

### 手动启动

```bash
# 构建并启动所有服务
docker compose up --build -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f
```

## 🌐 访问地址

- **前端应用**: http://localhost
- **后端 API**: http://localhost:3000
- **API 文档**: http://localhost:3000/docs

## 📁 项目结构

```
AI-Powered-ToDo-List/
├── backend/                     # 后端 API 服务
│   ├── src/                    # Python 源代码
│   │   ├── agents/             # AI 代理实现
│   │   ├── models/             # 数据模型
│   │   ├── routes/             # API 路由
│   │   └── services/           # 业务逻辑
│   ├── requirements.txt        # Python 依赖
│   ├── Dockerfile             # 后端 Docker 配置
│   └── .env                   # 环境变量
├── frontend/                   # 前端 React 应用
│   ├── src/                   # React 源代码
│   │   ├── components/        # React 组件
│   │   └── services/          # API 服务
│   ├── public/                # 静态资源
│   ├── package.json           # Node.js 依赖
│   └── Dockerfile             # 前端 Docker 配置
├── docker-compose.yml         # Docker Compose 配置
└── start-fullstack.sh         # 一键启动脚本
```

## 🛠️ 技术栈

### 后端
- **FastAPI**: 现代 Python Web 框架
- **LangGraph**: AI 代理框架
- **SQLite**: 轻量级数据库
- **Azure OpenAI**: AI 模型服务

### 前端
- **React 18**: 用户界面库
- **TypeScript**: 类型安全的 JavaScript
- **Ant Design**: 企业级 UI 组件库
- **Axios**: HTTP 客户端

### 部署
- **Docker**: 容器化技术
- **Docker Compose**: 多容器编排
- **Nginx**: 反向代理和静态文件服务

## 🔧 配置说明

### 环境变量

复制 `backend/env.example` 到 `backend/.env` 并配置：

```bash
# Azure OpenAI 配置
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 开发模式

```bash
# 后端开发
cd backend
uvicorn src.app:app --host 0.0.0.0 --port 3000 --reload

# 前端开发
cd frontend
npm start
```

## 📖 使用说明

### 传统任务管理（左侧）
- 点击"添加"按钮创建新任务
- 勾选复选框标记任务完成
- 点击"编辑"按钮修改任务标题
- 点击"删除"按钮删除任务

### AI 对话式管理（右侧）
- 在输入框中输入自然语言指令
- 例如："帮我创建一个学习 React 的任务"
- AI 助手会理解并执行相应操作
- 支持中文和英文对话

## 🐛 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 停止现有服务
   docker compose down
   
   # 检查端口占用
   netstat -tulpn | grep :80
   netstat -tulpn | grep :3000
   ```

2. **AI 功能不可用**
   - 检查 Azure OpenAI 配置
   - 查看后端日志：`docker compose logs backend`

3. **前端无法连接后端**
   - 检查网络连接：`docker compose ps`
   - 查看前端日志：`docker compose logs frontend`

### 日志查看

```bash
# 查看所有服务日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f backend
docker compose logs -f frontend
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License