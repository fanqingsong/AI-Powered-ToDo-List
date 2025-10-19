#!/bin/bash

echo "🛑 停止 AI Native 智能工作台服务..."

# 停止并删除容器
echo "🧹 停止并删除容器..."
docker stop ai-todo-backend ai-todo-frontend ai-todo-postgres 2>/dev/null || true
docker rm ai-todo-backend ai-todo-frontend ai-todo-postgres 2>/dev/null || true

# 删除网络
echo "🌐 删除网络..."
docker network rm ai-todo-network 2>/dev/null || true

echo "✅ 所有服务已停止！"
