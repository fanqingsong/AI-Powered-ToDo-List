#!/bin/bash

echo "🛑 停止 AI Native 智能工作台开发环境"
echo "================================================"

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，无需停止服务"
    exit 0
fi

# 检查 docker compose 是否可用
if ! command -v docker compose &> /dev/null; then
    echo "❌ docker compose 未安装"
    exit 1
fi

# 显示当前运行的服务
echo "🔍 检查当前运行的服务..."
docker compose ps

echo ""
echo "🛑 正在停止所有服务..."

# 停止所有服务
if docker compose down --remove-orphans; then
    echo "✅ 所有服务已停止"
else
    echo "⚠️  部分服务停止时出现问题，尝试强制停止..."
    
    # 强制停止可能残留的容器
    echo "🔨 强制停止残留容器..."
    docker rm -f ai-todo-postgres ai-todo-backend ai-todo-frontend ai-todo-redis ai-todo-weaviate ai-todo-weaviate-console ai-todo-celery-worker ai-todo-celery-beat ai-todo-flower 2>/dev/null || true
    
    # 清理网络
    echo "🌐 清理网络..."
    docker network rm ai-powered-todo-list_app-network ai-todo-network 2>/dev/null || true
fi

# 检查是否还有相关进程在运行
echo ""
echo "🔍 检查是否还有相关进程..."
remaining_processes=$(docker ps --filter "name=ai-todo" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || true)

if [ -n "$remaining_processes" ] && [ "$remaining_processes" != "NAMES	STATUS" ]; then
    echo "⚠️  发现残留的容器："
    echo "$remaining_processes"
    echo ""
    echo "🔨 强制清理残留容器..."
    docker ps --filter "name=ai-todo" --format "{{.Names}}" | xargs -r docker rm -f
else
    echo "✅ 所有相关容器已清理"
fi

# 检查端口占用
echo ""
echo "🔍 检查端口占用情况..."
ports=(3000 3001 5432 6379 8080 8081 5555)
occupied_ports=()

for port in "${ports[@]}"; do
    if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
        occupied_ports+=($port)
    fi
done

if [ ${#occupied_ports[@]} -gt 0 ]; then
    echo "⚠️  以下端口仍被占用：${occupied_ports[*]}"
    echo "💡 如需释放端口，请检查相关进程："
    for port in "${occupied_ports[@]}"; do
        echo "   端口 $port: netstat -tlnp | grep :$port"
    done
else
    echo "✅ 所有端口已释放"
fi

# 显示清理结果
echo ""
echo "📊 清理结果："
echo "================================================"

# 检查容器状态
echo "🐳 容器状态："
if docker ps --filter "name=ai-todo" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null | grep -q "ai-todo"; then
    docker ps --filter "name=ai-todo" --format "table {{.Names}}\t{{.Status}}"
else
    echo "✅ 无运行中的 AI Native 容器"
fi

# 检查网络状态
echo ""
echo "🌐 网络状态："
if docker network ls --filter "name=ai-powered-todo-list" --format "table {{.Name}}\t{{.Driver}}" 2>/dev/null | grep -q "ai-powered-todo-list"; then
    docker network ls --filter "name=ai-powered-todo-list" --format "table {{.Name}}\t{{.Driver}}"
else
    echo "✅ AI Native 网络已清理"
fi

# 检查数据卷状态
echo ""
echo "💾 数据卷状态："
if docker volume ls --filter "name=ai-powered-todo-list" --format "table {{.Name}}\t{{.Driver}}" 2>/dev/null | grep -q "ai-powered-todo-list"; then
    docker volume ls --filter "name=ai-powered-todo-list" --format "table {{.Name}}\t{{.Driver}}"
    echo "💡 数据卷已保留，重启时会恢复数据"
else
    echo "✅ 无 AI Native 数据卷"
fi

echo ""
echo "🎉 开发环境已完全停止！"
echo "================================================"
echo ""
echo "📚 常用命令："
echo "   ./start-dev.sh           # 重新启动开发环境"
echo "   ./start-dev.sh -f        # 强制清理后启动"
echo "   ./clean-all.sh           # 清理所有资源（保留数据）"
echo "   ./clean-all.sh --with-volumes  # 完全清理（包括数据）"
echo ""
echo "🔧 故障排除："
echo "   如果端口仍被占用：netstat -tlnp | grep -E ':(3000|3001|5432|6379|8080|8081|5555)'"
echo "   如果需要强制清理：./clean-all.sh --with-volumes"
echo "   如果遇到权限问题：sudo docker compose down"
echo "================================================"
