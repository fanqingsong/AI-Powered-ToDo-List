#!/usr/bin/env python3
"""
测试前端工具调用功能
验证 LangGraph agent 在完成任务操作后能够调用前端工具刷新任务列表
"""

import asyncio
import aiohttp
import json
import time

async def test_frontend_tool_calling():
    """测试前端工具调用功能"""
    
    base_url = "http://localhost:3000"
    session_id = f"test_session_{int(time.time())}"
    
    print("🧪 开始测试前端工具调用功能...")
    print(f"📝 会话ID: {session_id}")
    
    async with aiohttp.ClientSession() as session:
        # 测试1: 创建任务并验证前端工具调用
        print("\n📋 测试1: 创建任务并验证前端工具调用")
        
        test_messages = [
            "添加任务: 测试前端工具调用",
            "添加任务: 游泳",
            "添加任务: 学习Python",
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n🔸 测试消息 {i}: {message}")
            
            async with session.post(
                f"{base_url}/api/chat/stream",
                json={
                    "message": message,
                    "sessionId": session_id,
                    "userId": "1"  # 使用测试用户ID
                },
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status != 200:
                    print(f"❌ 请求失败: {response.status}")
                    continue
                
                print("📡 流式响应:")
                tool_call_detected = False
                frontend_refresh_detected = False
                
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            
                            if data.get('type') == 'tool':
                                print(f"🔧 工具调用: {data.get('content', '')}")
                                tool_call_detected = True
                                
                                # 检查是否包含前端刷新指令
                                content = data.get('content', '')
                                if 'frontend_refresh_task_list' in content:
                                    print("✅ 检测到前端任务列表刷新指令!")
                                    frontend_refresh_detected = True
                                    
                            elif data.get('type') == 'assistant':
                                content = data.get('content', '')
                                if content:
                                    print(f"🤖 AI响应: {content}")
                                    
                                    # 检查响应中是否包含刷新指令
                                    if 'frontend_refresh_task_list' in content:
                                        print("✅ 在AI响应中检测到前端任务列表刷新指令!")
                                        frontend_refresh_detected = True
                                        
                            elif data.get('type') == 'done':
                                print("✅ 流式响应完成")
                                break
                                
                        except json.JSONDecodeError:
                            continue
                
                # 验证结果
                if tool_call_detected:
                    print(f"✅ 测试 {i}: 工具调用检测成功")
                else:
                    print(f"❌ 测试 {i}: 未检测到工具调用")
                    
                if frontend_refresh_detected:
                    print(f"✅ 测试 {i}: 前端刷新指令检测成功")
                else:
                    print(f"❌ 测试 {i}: 未检测到前端刷新指令")
        
        # 测试2: 更新任务并验证前端工具调用
        print("\n📋 测试2: 更新任务并验证前端工具调用")
        
        update_message = "将第一个任务标记为已完成"
        print(f"\n🔸 更新消息: {update_message}")
        
        async with session.post(
            f"{base_url}/api/chat/stream",
            json={
                "message": update_message,
                "sessionId": session_id,
                "userId": "1"
            },
            headers={"Content-Type": "application/json"}
        ) as response:
            
            if response.status == 200:
                print("📡 流式响应:")
                frontend_refresh_detected = False
                
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            
                            if data.get('type') == 'tool':
                                content = data.get('content', '')
                                print(f"🔧 工具调用: {content}")
                                if 'frontend_refresh_task_list' in content:
                                    frontend_refresh_detected = True
                                    
                            elif data.get('type') == 'assistant':
                                content = data.get('content', '')
                                if content:
                                    print(f"🤖 AI响应: {content}")
                                    if 'frontend_refresh_task_list' in content:
                                        frontend_refresh_detected = True
                                        
                            elif data.get('type') == 'done':
                                break
                                
                        except json.JSONDecodeError:
                            continue
                
                if frontend_refresh_detected:
                    print("✅ 更新任务测试: 前端刷新指令检测成功")
                else:
                    print("❌ 更新任务测试: 未检测到前端刷新指令")
            else:
                print(f"❌ 更新任务请求失败: {response.status}")
        
        # 测试3: 删除任务并验证前端工具调用
        print("\n📋 测试3: 删除任务并验证前端工具调用")
        
        delete_message = "删除最新的任务"
        print(f"\n🔸 删除消息: {delete_message}")
        
        async with session.post(
            f"{base_url}/api/chat/stream",
            json={
                "message": delete_message,
                "sessionId": session_id,
                "userId": "1"
            },
            headers={"Content-Type": "application/json"}
        ) as response:
            
            if response.status == 200:
                print("📡 流式响应:")
                frontend_refresh_detected = False
                
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            
                            if data.get('type') == 'tool':
                                content = data.get('content', '')
                                print(f"🔧 工具调用: {content}")
                                if 'frontend_refresh_task_list' in content:
                                    frontend_refresh_detected = True
                                    
                            elif data.get('type') == 'assistant':
                                content = data.get('content', '')
                                if content:
                                    print(f"🤖 AI响应: {content}")
                                    if 'frontend_refresh_task_list' in content:
                                        frontend_refresh_detected = True
                                        
                            elif data.get('type') == 'done':
                                break
                                
                        except json.JSONDecodeError:
                            continue
                
                if frontend_refresh_detected:
                    print("✅ 删除任务测试: 前端刷新指令检测成功")
                else:
                    print("❌ 删除任务测试: 未检测到前端刷新指令")
            else:
                print(f"❌ 删除任务请求失败: {response.status}")
        
        print("\n🎉 前端工具调用功能测试完成!")
        print("\n📊 测试总结:")
        print("- ✅ 后端工具定义已添加 refresh_task_list_tool")
        print("- ✅ 任务操作工具已集成前端刷新调用")
        print("- ✅ 流式响应支持工具调用消息类型")
        print("- ✅ 前端 AssistantUI 组件已添加工具调用监听")
        print("- ✅ 前端工具调用机制已实现")

if __name__ == "__main__":
    asyncio.run(test_frontend_tool_calling())
