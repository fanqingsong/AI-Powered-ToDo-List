#!/bin/bash

# AI-Powered ToDo List 启动脚本
# 用于启动所有服务

echo "🚀 启动 AI-Powered ToDo List..."

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 检查 docker-compose 是否可用
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose 未安装，请先安装 docker-compose"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p logs
mkdir -p data

# 检查环境变量文件
if [ ! -f "backend/.env" ]; then
    echo "⚠️  未找到 backend/.env 文件，请复制 backend/.env.example 并配置"
    echo "   特别是 OPENAI_API_KEY 需要配置"
fi

# 启动服务
echo "🐳 启动 Docker 服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 显示服务访问信息
echo ""
echo "✅ 服务启动完成！"
echo ""
echo "📋 服务访问信息："
echo "   - 前端应用: http://localhost:3001"
echo "   - 后端API: http://localhost:3000"
echo "   - API文档: http://localhost:3000/docs"
echo "   - Weaviate: http://localhost:8080"
echo "   - Redis: localhost:6379"
echo "   - PostgreSQL: localhost:5432"
echo ""
echo "🔧 管理命令："
echo "   - 查看日志: docker-compose logs -f"
echo "   - 停止服务: docker-compose down"
echo "   - 重启服务: docker-compose restart"
echo "   - 查看状态: docker-compose ps"
echo ""
echo "📚 智能搜索功能："
echo "   - 确保已配置 OPENAI_API_KEY"
echo "   - 首次使用需要等待向量数据库同步"
echo "   - 可以在前端笔记管理页面使用智能搜索"
echo ""