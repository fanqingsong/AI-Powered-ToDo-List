#!/bin/bash

echo "🚀 启动 AI 智能任务管理器 (生产模式)"
echo "================================================"

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 检查 docker compose 是否可用
if ! command -v docker compose &> /dev/null; then
    echo "❌ docker compose 未安装，请先安装 Docker Compose"
    exit 1
fi

echo "📦 构建并启动服务..."

# 停止现有容器
echo "🛑 停止现有容器..."
docker compose down --remove-orphans

# 构建并启动服务
echo "🏗️ 构建并启动服务..."
docker compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker compose ps

# 检查后端健康状态
echo "🏥 检查后端健康状态..."
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo "✅ 后端服务运行正常"
else
    echo "❌ 后端服务启动失败"
    docker compose logs backend
    exit 1
fi

# 检查前端服务
echo "🌐 检查前端服务..."
if curl -s http://localhost:80 > /dev/null; then
    echo "✅ 前端服务运行正常"
else
    echo "❌ 前端服务启动失败"
    docker compose logs frontend
    exit 1
fi

echo ""
echo "🎉 应用启动成功！"
echo "================================================"
echo "🌐 前端访问地址: http://localhost"
echo "🔧 后端 API 地址: http://localhost:3000"
echo "📚 API 文档地址: http://localhost:3000/docs"
echo ""
echo "💡 使用说明："
echo "   - 左侧：传统任务管理（手动添加、编辑、删除任务）"
echo "   - 右侧：AI 对话式管理（与 AI 助手对话管理任务）"
echo ""
echo "🛑 停止应用: docker compose down"
echo "📊 查看日志: docker compose logs -f"
echo "================================================"
