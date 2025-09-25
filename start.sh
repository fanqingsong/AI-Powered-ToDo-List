#!/bin/bash

# AI-Powered ToDo List 启动脚本

echo "🚀 启动 AI-Powered ToDo List..."

# 检测网络连接和镜像源
echo "🔍 检测网络连接..."
if ping -c 1 mirrors.aliyun.com > /dev/null 2>&1; then
    echo "✅ 阿里云镜像源连接正常"
else
    echo "⚠️  阿里云镜像源连接异常，可能影响构建速度"
fi

if ping -c 1 pypi.tuna.tsinghua.edu.cn > /dev/null 2>&1; then
    echo "✅ 清华大学 pip 镜像源连接正常"
else
    echo "⚠️  清华大学 pip 镜像源连接异常，可能影响包安装速度"
fi

# 检查是否存在 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件，正在从 env.example 创建..."
    cp env.example .env
    echo "📝 请编辑 .env 文件，填入您的 Azure 配置信息"
    echo "   然后重新运行此脚本"
    exit 1
fi

# 创建数据目录
mkdir -p data

# 启动 Docker Compose
echo "🐳 启动 Docker 容器..."
docker compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
if docker compose ps | grep -q "Up"; then
    echo "✅ 服务启动成功！"
    echo "🌐 应用访问地址: http://localhost:3000"
    echo "📊 查看日志: docker compose logs -f"
    echo "🛑 停止服务: docker compose down"
else
    echo "❌ 服务启动失败，请检查日志: docker compose logs"
    exit 1
fi
