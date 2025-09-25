#!/bin/bash

echo "🔨 构建前端应用..."

# 进入前端目录
cd frontend

# 安装依赖
echo "📦 安装依赖..."
npm install

# 构建应用
echo "🏗️ 构建应用..."
npm run build

# 检查构建结果
if [ -d "build" ]; then
    echo "✅ 前端构建成功！"
    echo "📁 构建文件位于: frontend/build/"
else
    echo "❌ 前端构建失败！"
    exit 1
fi

echo "🎉 前端构建完成！"
