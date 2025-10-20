#!/bin/bash

# AI助手智能程度测试脚本 - 基于登录用户信息
echo "🤖 测试AI助手的智能程度提升（基于登录用户信息）..."

# 测试用户身份识别
echo "📝 测试1: 用户身份识别（基于登录信息）"
curl -X POST http://localhost:3000/api/chat/foundry \
  -H "Content-Type: application/json" \
  -d '{
    "message": "我是谁？",
    "session_id": "test_session_001",
    "user_id": "1"
  }' | jq -r '.content'

echo -e "\n📝 测试2: 个性化服务（基于用户信息）"
curl -X POST http://localhost:3000/api/chat/foundry \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你知道我的基本信息吗？",
    "session_id": "test_session_001", 
    "user_id": "1"
  }' | jq -r '.content'

echo -e "\n📝 测试3: 智能任务管理"
curl -X POST http://localhost:3000/api/chat/foundry \
  -H "Content-Type: application/json" \
  -d '{
    "message": "帮我创建一个学习AI的任务",
    "session_id": "test_session_001",
    "user_id": "1"
  }' | jq -r '.content'

echo -e "\n📝 测试4: 用户信息展示"
curl -X POST http://localhost:3000/api/chat/foundry \
  -H "Content-Type: application/json" \
  -d '{
    "message": "告诉我关于我的详细信息",
    "session_id": "test_session_001",
    "user_id": "1"
  }' | jq -r '.content'

echo -e "\n✅ AI助手智能程度测试完成！"
