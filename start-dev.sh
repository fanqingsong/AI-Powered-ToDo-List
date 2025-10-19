#!/bin/bash

echo "🚀 启动 AI Native 智能工作台 (开发模式 - 支持热重载)"
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

# 清理现有容器和网络
echo "🧹 清理现有容器和网络..."

# 检查是否存在清理脚本，如果存在则使用它
if [ -f "./clean-all.sh" ]; then
    echo "🔧 使用完整清理脚本..."
    ./clean-all.sh
else
    # 手动清理
    echo "🛑 停止现有容器..."
    docker compose down --remove-orphans 2>/dev/null || true

    # 强制删除可能存在的同名容器
    echo "🗑️ 强制删除同名容器..."
    docker rm -f ai-todo-postgres ai-todo-backend ai-todo-frontend 2>/dev/null || true

    # 删除可能存在的网络
    echo "🌐 清理网络..."
    docker network rm ai-powered-todo-list_app-network ai-todo-network 2>/dev/null || true

    # 等待清理完成
    sleep 2
fi

# 构建并启动开发服务（使用 watch 模式）
echo "🏗️ 构建并启动开发服务（watch 模式）..."

# 尝试启动服务，如果失败则重试
max_retries=3
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    echo "🔄 尝试启动服务 (第 $((retry_count + 1)) 次)..."
    
    if docker compose up --build -d; then
        echo "✅ 服务启动成功"
        break
    else
        echo "❌ 服务启动失败，正在重试..."
        retry_count=$((retry_count + 1))
        
        if [ $retry_count -lt $max_retries ]; then
            echo "🧹 清理后重试..."
            docker compose down --remove-orphans 2>/dev/null || true
            docker rm -f ai-todo-postgres ai-todo-backend ai-todo-frontend 2>/dev/null || true
            sleep 3
        else
            echo "❌ 服务启动失败，已达到最大重试次数"
            echo "🔍 查看详细错误信息："
            docker compose logs
            exit 1
        fi
    fi
done

# 在启动 docker compose 服务前，强制重新构建所有服务镜像
echo "🔨 重新编译所有服务镜像..."
docker compose build --no-cache

# 启动 watch 模式
echo "👀 启动文件监听模式..."
docker compose watch

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

# 检查服务状态
echo "🔍 检查服务状态..."
docker compose ps

# 检查服务健康状态
echo "🏥 检查服务健康状态..."

# 等待服务完全启动
echo "⏳ 等待服务完全启动..."
sleep 10

# 检查后端健康状态
echo "🔧 检查后端服务..."
backend_healthy=false
for i in {1..10}; do
    if curl -s http://localhost:3000/ > /dev/null 2>&1; then
        echo "✅ 后端服务运行正常"
        backend_healthy=true
        break
    else
        echo "⏳ 等待后端服务启动... ($i/10)"
        sleep 3
    fi
done

if [ "$backend_healthy" = false ]; then
    echo "❌ 后端服务启动失败"
    echo "🔍 后端服务日志："
    docker compose logs backend --tail 20
    exit 1
fi

# 检查前端服务
echo "🌐 检查前端服务..."
frontend_healthy=false
for i in {1..10}; do
    if curl -s http://localhost:3001 > /dev/null 2>&1; then
        echo "✅ 前端服务运行正常"
        frontend_healthy=true
        break
    else
        echo "⏳ 等待前端服务启动... ($i/10)"
        sleep 3
    fi
done

if [ "$frontend_healthy" = false ]; then
    echo "❌ 前端服务启动失败"
    echo "🔍 前端服务日志："
    docker compose logs frontend --tail 20
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
echo "🧹 完全清理环境: ./stop-services.sh"
echo "📊 查看日志: docker compose logs -f"
echo "🔍 查看特定服务日志: docker compose logs -f backend|frontend"
echo ""
echo "🔧 故障排除："
echo "   如果遇到容器名称冲突，请运行: ./stop-services.sh"
echo "   如果服务启动失败，请检查端口占用: netstat -tlnp | grep -E ':(3000|3001|5432)'"
echo "   如果数据库连接失败，请检查: docker logs ai-todo-postgres"
echo "================================================"
