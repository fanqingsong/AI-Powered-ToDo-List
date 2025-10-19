#!/bin/bash

echo "🚀 启动 AI Native 智能工作台服务..."

# 清理现有容器
echo "🧹 清理现有容器..."
docker stop ai-todo-backend ai-todo-frontend ai-todo-postgres 2>/dev/null || true
docker rm ai-todo-backend ai-todo-frontend ai-todo-postgres 2>/dev/null || true

# 创建网络
echo "🌐 创建网络..."
docker network create ai-todo-network 2>/dev/null || true

# 启动数据库
echo "🗄️  启动数据库..."
docker run -d --name ai-todo-postgres \
  --network ai-todo-network \
  -p 5432:5432 \
  -e POSTGRES_DB=ai_todo_db \
  -e POSTGRES_USER=ai_todo_user \
  -e POSTGRES_PASSWORD=ai_todo_password \
  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/postgres:15-alpine

# 等待数据库启动
echo "⏳ 等待数据库启动..."
sleep 5

# 启动后端
echo "🔧 启动后端服务..."
docker run -d --name ai-todo-backend \
  --network ai-todo-network \
  -p 3000:3000 \
  -e DATABASE_URL=postgresql://ai_todo_user:ai_todo_password@ai-todo-postgres:5432/ai_todo_db \
  ai-powered-todo-list_backend

# 启动前端
echo "🎨 启动前端服务..."
docker run -d --name ai-todo-frontend \
  --network ai-todo-network \
  -p 3001:3000 \
  ai-powered-todo-list_frontend

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo "📊 检查服务状态..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "✅ 服务启动完成！"
echo "🌐 前端地址: http://localhost:3001"
echo "🔧 后端地址: http://localhost:3000"
echo "📚 API文档: http://localhost:3000/docs"
echo ""
echo "💡 使用以下命令查看日志："
echo "   docker logs ai-todo-frontend"
echo "   docker logs ai-todo-backend"
echo "   docker logs ai-todo-postgres"
