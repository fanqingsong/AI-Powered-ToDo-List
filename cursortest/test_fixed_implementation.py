#!/usr/bin/env python3
"""
测试修复后的前端工具调用功能
验证使用自定义事件实现任务刷新
"""

import time
import requests
import json

def test_fixed_frontend_tool_calling():
    """测试修复后的前端工具调用功能"""
    
    print("🔍 测试修复后的前端工具调用功能")
    print("=" * 50)
    
    base_url = "http://localhost:3000"
    session_id = f"test_session_fixed_{int(time.time())}"
    
    print(f"📝 会话ID: {session_id}")
    
    # 测试1: 创建任务并验证前端工具调用
    print("\n📋 测试1: 创建任务并验证前端工具调用")
    
    test_message = "添加任务: 测试修复后的前端工具调用"
    print(f"🔸 测试消息: {test_message}")
    
    try:
        response = requests.post(
            f"{base_url}/api/chat/stream",
            json={
                "message": test_message,
                "sessionId": session_id,
                "userId": "1"
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code}")
            return
        
        print("📡 流式响应:")
        tool_call_detected = False
        frontend_tool_detected = False
        
        for line in response.text.split('\n'):
            line = line.strip()
            
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    
                    if data.get('type') == 'tool':
                        content = data.get('content', '')
                        print(f"🔧 工具调用: {content}")
                        tool_call_detected = True
                        
                        # 检查是否包含前端工具调用
                        if 'frontend_refresh_task_list' in content.lower() or '刷新任务列表' in content.lower():
                            print("✅ 检测到前端工具调用!")
                            frontend_tool_detected = True
                            
                    elif data.get('type') == 'assistant':
                        content = data.get('content', '')
                        if content:
                            print(f"🤖 AI响应: {content}")
                            
                    elif data.get('type') == 'done':
                        print("✅ 流式响应完成")
                        break
                        
                except json.JSONDecodeError:
                    continue
        
        # 验证结果
        if tool_call_detected:
            print(f"✅ 工具调用检测成功")
        else:
            print(f"❌ 未检测到工具调用")
            
        if frontend_tool_detected:
            print(f"✅ 前端工具调用检测成功")
        else:
            print(f"❌ 未检测到前端工具调用")
    
    except Exception as e:
        print(f"❌ 测试异常: {e}")
    
    # 测试2: 检查任务是否创建成功
    print("\n📋 测试2: 检查任务是否创建成功")
    
    try:
        response = requests.get(f"{base_url}/api/tasks", timeout=5)
        if response.status_code == 200:
            tasks = response.json()
            print(f"✅ 当前任务数量: {len(tasks)}")
            
            # 查找测试任务
            test_task = None
            for task in tasks:
                if '测试修复后的前端工具调用' in task.get('title', ''):
                    test_task = task
                    break
            
            if test_task:
                print(f"✅ 测试任务创建成功: {test_task['title']} (ID: {test_task['id']})")
            else:
                print("❌ 未找到测试任务")
        else:
            print(f"❌ 获取任务失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 检查任务异常: {e}")
    
    print("\n🎯 修复后的实现特点:")
    print("   ✅ 移除了复杂的 assistant-ui runtime 依赖")
    print("   ✅ 使用简单的自定义事件通信")
    print("   ✅ 通过 AssistantUI 组件监听后端响应")
    print("   ✅ 通过 FrontendTools 组件触发前端操作")
    
    print("\n💡 实现说明:")
    print("   1. 后端返回包含特殊标识的响应")
    print("   2. AssistantUI 组件监听响应并触发自定义事件")
    print("   3. FrontendTools 组件监听自定义事件")
    print("   4. TaskManager 组件监听刷新事件并更新列表")
    
    print("\n🔧 技术细节:")
    print("   - 后端: 返回 'frontend_refresh_task_list' 标识")
    print("   - AssistantUI: 监听消息并触发 'backendRefreshSignal' 事件")
    print("   - FrontendTools: 监听 'backendRefreshSignal' 并触发 'refreshTaskList' 事件")
    print("   - TaskManager: 监听 'refreshTaskList' 事件并刷新任务列表")
    
    print("\n🎉 优势:")
    print("   - 无需复杂的 assistant-ui runtime 配置")
    print("   - 使用标准的浏览器事件系统")
    print("   - 代码更简单，更容易理解和维护")
    print("   - 避免了 assistant-ui 的上下文依赖问题")

if __name__ == "__main__":
    test_fixed_frontend_tool_calling()
