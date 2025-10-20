#!/bin/bash

echo "=== 测试会话历史持久化功能 ==="
echo

# 测试1: 发送消息并创建会话历史
echo "1. 创建新的会话历史..."
curl -X POST "http://localhost:3000/api/chat/langgraph" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "添加一个任务：测试会话持久化",
    "sessionId": "persistence_test_session",
    "userId": "test_user_persistence"
  }' | jq .

echo
echo "2. 继续对话..."
curl -X POST "http://localhost:3000/api/chat/langgraph" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "查看所有任务",
    "sessionId": "persistence_test_session",
    "userId": "test_user_persistence"
  }' | jq .

echo
echo "3. 获取会话历史..."
curl -X GET "http://localhost:3000/api/conversations/persistence_test_session?user_id=test_user_persistence" | jq .

echo
echo "4. 获取会话统计..."
curl -X GET "http://localhost:3000/api/conversations/stats/persistence_test_session?user_id=test_user_persistence" | jq .

echo
echo "5. 测试会话历史API端点..."
echo "   - 获取会话历史: GET /api/conversations/{sessionId}"
echo "   - 清空会话历史: DELETE /api/conversations/{sessionId}"
echo "   - 获取会话统计: GET /api/conversations/stats/{sessionId}"
echo "   - 获取用户会话: GET /api/conversations/user/{userId}"

echo
echo "=== 测试完成 ==="
echo "现在您可以："
echo "1. 打开浏览器访问 http://localhost:3001"
echo "2. 在AI助手中发送消息"
echo "3. 刷新页面，会话历史应该会自动加载"
echo "4. 使用'清空对话'按钮测试清空功能"
