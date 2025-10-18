#!/bin/bash

echo "🚀 启动 AI Native 智能工作台 (Watch 模式)"
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

echo ""
echo "🎉 服务启动成功！"
echo "================================================"
echo "🌐 前端开发地址: http://localhost:3001"
echo "🔧 后端 API 地址: http://localhost:3000"
echo "📚 API 文档地址: http://localhost:3000/docs"
echo ""
echo "💡 Watch 模式特性："
echo "   - 🔥 前端热重载：修改 React 代码自动刷新"
echo "   - 🔄 后端热重载：修改 Python 代码自动重启"
echo "   - 📁 文件同步：实时同步本地文件到容器"
echo ""
echo "👀 启动文件监听模式..."
echo "按 Ctrl+C 停止监听"
echo "================================================"

# 启动 watch 模式
docker compose watch
