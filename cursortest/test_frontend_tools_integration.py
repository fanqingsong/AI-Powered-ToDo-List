#!/usr/bin/env python3
"""
测试前端工具集成功能
"""

import asyncio
import json
import requests
from typing import Dict, Any, List

# 测试配置
BASE_URL = "http://localhost:3000"
TEST_USER_ID = "1"
TEST_SESSION_ID = "test_session_123"

def test_frontend_tools_config():
    """测试前端工具配置"""
    print("🧪 测试前端工具配置...")
    
    # 前端工具配置
    frontend_tools_config = [
        {
            "name": "show_notification",
            "description": "在前端显示通知消息"
        },
        {
            "name": "open_modal", 
            "description": "在前端打开模态框"
        },
        {
            "name": "update_ui_state",
            "description": "更新前端UI状态"
        }
    ]
    
    return frontend_tools_config

def test_chat_with_frontend_tools():
    """测试带前端工具配置的聊天"""
    print("🧪 测试带前端工具配置的聊天...")
    
    frontend_tools_config = test_frontend_tools_config()
    
    # 测试消息
    test_messages = [
        "请显示一个通知",
        "打开一个模态框",
        "更新UI状态",
        "创建一个新任务：测试前端工具集成"
    ]
    
    for message in test_messages:
        print(f"\n📝 发送消息: {message}")
        
        # 构建请求
        chat_request = {
            "message": message,
            "sessionId": TEST_SESSION_ID,
            "userId": TEST_USER_ID,
            "frontend_tools_config": frontend_tools_config
        }
        
        try:
            # 发送请求
            response = requests.post(
                f"{BASE_URL}/api/chat/stream",
                json=chat_request,
                headers={"Content-Type": "application/json"},
                stream=True,
                timeout=30
            )
            
            if response.status_code == 200:
                print("✅ 请求成功，开始接收流式响应...")
                
                # 处理流式响应
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            try:
                                data = json.loads(line_str[6:])
                                
                                if data.get('type') == 'frontend_tool':
                                    print(f"🎯 前端工具调用: {data.get('tool_name')}")
                                    print(f"   内容: {data.get('content')}")
                                elif data.get('type') == 'assistant':
                                    content = data.get('content', '')
                                    if content:
                                        print(f"🤖 AI响应: {content}")
                                elif data.get('type') == 'tool':
                                    print(f"🔧 工具调用: {data.get('content')}")
                                elif data.get('type') == 'done':
                                    print("✅ 响应完成")
                                    break
                                elif data.get('type') == 'error':
                                    print(f"❌ 错误: {data.get('content')}")
                                    
                            except json.JSONDecodeError as e:
                                print(f"⚠️ JSON解析错误: {e}")
                                print(f"   原始数据: {line_str}")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"   响应: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
        
        print("-" * 50)

def test_backend_health():
    """测试后端健康状态"""
    print("🧪 测试后端健康状态...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            return True
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到后端服务: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试前端工具集成功能")
    print("=" * 60)
    
    # 检查后端健康状态
    if not test_backend_health():
        print("❌ 后端服务不可用，请先启动后端服务")
        return
    
    print("\n" + "=" * 60)
    
    # 测试前端工具配置
    frontend_tools_config = test_frontend_tools_config()
    print(f"✅ 前端工具配置: {len(frontend_tools_config)} 个工具")
    for tool in frontend_tools_config:
        print(f"   - {tool['name']}: {tool['description']}")
    
    print("\n" + "=" * 60)
    
    # 测试聊天功能
    test_chat_with_frontend_tools()
    
    print("\n" + "=" * 60)
    print("🎉 前端工具集成测试完成")

if __name__ == "__main__":
    main()
