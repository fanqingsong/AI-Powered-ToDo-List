#!/bin/bash

echo "🚀 启动 AI 智能任务管理器 (开发模式 - 支持热重载)"
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

echo "📦 构建并启动开发服务..."

# 停止现有容器
echo "🛑 停止现有容器..."
docker compose down --remove-orphans

# 构建并启动开发服务（使用 watch 模式）
echo "🏗️ 构建并启动开发服务（watch 模式）..."
docker compose up --build -d

# 启动 watch 模式
echo "👀 启动文件监听模式..."
docker compose watch

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

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
if curl -s http://localhost:3001 > /dev/null; then
    echo "✅ 前端服务运行正常"
else
    echo "❌ 前端服务启动失败"
    docker compose logs frontend
    exit 1
fi

echo ""
echo "🎉 开发环境启动成功！"
echo "================================================"
echo "🌐 前端开发地址: http://localhost:3001"
echo "🔧 后端 API 地址: http://localhost:3000"
echo "📚 API 文档地址: http://localhost:3000/docs"
echo ""
echo "💡 开发模式特性："
echo "   - 🔥 前端热重载：修改 React 代码自动刷新"
echo "   - 🔄 后端热重载：修改 Python 代码自动重启"
echo "   - 📁 文件监听：实时同步本地文件到容器"
echo ""
echo "🛑 停止开发环境: docker compose down"
echo "📊 查看日志: docker compose logs -f"
echo "🔍 查看特定服务日志: docker compose logs -f backend|frontend"
echo "================================================"
