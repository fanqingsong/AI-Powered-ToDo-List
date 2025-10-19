#!/bin/bash

echo "🧹 AI Native 智能工作台 - 完全清理脚本"
echo "================================================"

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

echo "🛑 停止所有相关容器..."

# 停止所有相关容器
docker stop ai-todo-postgres ai-todo-backend ai-todo-frontend 2>/dev/null || true

# 删除所有相关容器
echo "🗑️ 删除所有相关容器..."
docker rm -f ai-todo-postgres ai-todo-backend ai-todo-frontend 2>/dev/null || true

# 停止并删除 docker compose 服务
echo "📦 停止 Docker Compose 服务..."
docker compose down --remove-orphans --volumes 2>/dev/null || true

# 删除所有相关网络
echo "🌐 删除相关网络..."
docker network rm ai-powered-todo-list_app-network ai-todo-network 2>/dev/null || true

# 清理悬空镜像
echo "🖼️ 清理悬空镜像..."
docker image prune -f 2>/dev/null || true

# 清理未使用的卷
echo "💾 清理未使用的卷..."
docker volume prune -f 2>/dev/null || true

# 检查端口占用
echo "🔍 检查端口占用..."
if netstat -tlnp 2>/dev/null | grep -E ':(3000|3001|5432)' > /dev/null; then
    echo "⚠️ 发现端口占用："
    netstat -tlnp 2>/dev/null | grep -E ':(3000|3001|5432)'
    echo ""
    echo "💡 如果端口被其他进程占用，请手动停止相关进程"
else
    echo "✅ 端口 3000, 3001, 5432 未被占用"
fi

# 显示清理结果
echo ""
echo "🔍 清理结果检查："
echo "📦 相关容器："
docker ps -a --filter "name=ai-todo" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "   无相关容器"

echo ""
echo "🌐 相关网络："
docker network ls --filter "name=ai-todo" --format "table {{.Name}}\t{{.Driver}}" 2>/dev/null || echo "   无相关网络"

echo ""
echo "✅ 清理完成！"
echo "================================================"
echo "💡 现在可以运行以下命令重新启动："
echo "   ./start-dev.sh    # 开发模式"
echo "   ./start-services.sh  # 生产模式"
echo "================================================"
