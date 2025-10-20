#!/bin/bash

echo "⚡ AI Native 智能工作台 - 快速启动脚本"
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

echo "🚀 快速启动服务（不清理现有容器）..."

# 检查服务是否已经在运行
if docker compose ps | grep -q "Up"; then
    echo "✅ 服务已在运行中"
    echo "🌐 前端地址: http://localhost:3001"
    echo "🔧 后端地址: http://localhost:3000"
    echo "📚 API 文档: http://localhost:3000/docs"
    exit 0
fi

# 启动服务（不重新构建）
echo "🏗️ 启动服务..."
if docker compose up -d; then
    echo "✅ 服务启动成功"
else
    echo "❌ 服务启动失败，尝试重新构建..."
    docker compose up --build -d
fi

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker compose ps

# 检查服务健康状态
echo "🏥 检查服务健康状态..."

# 检查后端健康状态
echo "🔧 检查后端服务..."
backend_healthy=false
for i in {1..5}; do
    if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        echo "✅ 后端服务运行正常"
        backend_healthy=true
        break
    else
        echo "⏳ 等待后端服务启动... ($i/5)"
        sleep 3
    fi
done

if [ "$backend_healthy" = false ]; then
    echo "❌ 后端服务启动失败"
    echo "🔍 后端服务日志："
    docker compose logs backend --tail 10
    exit 1
fi

# 检查前端服务
echo "🌐 检查前端服务..."
frontend_healthy=false
for i in {1..5}; do
    if curl -s http://localhost:3001 > /dev/null 2>&1; then
        echo "✅ 前端服务运行正常"
        frontend_healthy=true
        break
    else
        echo "⏳ 等待前端服务启动... ($i/5)"
        sleep 3
    fi
done

if [ "$frontend_healthy" = false ]; then
    echo "❌ 前端服务启动失败"
    echo "🔍 前端服务日志："
    docker compose logs frontend --tail 10
    exit 1
fi

echo ""
echo "🎉 快速启动成功！"
echo "================================================"
echo "🌐 前端开发地址: http://localhost:3001"
echo "🔧 后端 API 地址: http://localhost:3000"
echo "📚 API 文档地址: http://localhost:3000/docs"
echo ""
echo "💡 快速启动特性："
echo "   - ⚡ 不清理现有容器和数据"
echo "   - 🚀 启动速度更快"
echo "   - 💾 保留所有数据"
echo ""
echo "🛑 停止服务: docker compose down"
echo "📊 查看日志: docker compose logs -f"
echo "🔄 重启服务: docker compose restart"
echo "================================================"
