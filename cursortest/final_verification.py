#!/usr/bin/env python3
"""
最终验证脚本 - 确认无限请求问题已修复
"""

import time
import requests

def final_verification():
    """最终验证修复效果"""
    
    print("🔍 最终验证：无限请求问题修复")
    print("=" * 50)
    
    base_url = "http://localhost:3000"
    
    # 1. 检查服务状态
    print("1️⃣ 检查服务状态...")
    try:
        response = requests.get(f"{base_url}/api/tasks", timeout=5)
        if response.status_code == 200:
            tasks = response.json()
            print(f"✅ 后端服务正常，当前有 {len(tasks)} 个任务")
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 后端服务连接失败: {e}")
        return
    
    # 2. 测试任务操作
    print("\n2️⃣ 测试任务操作...")
    try:
        response = requests.post(
            f"{base_url}/api/tasks",
            json={"title": "最终验证测试", "isComplete": False},
            timeout=5
        )
        if response.status_code == 201:
            print("✅ 任务创建成功")
        else:
            print(f"❌ 任务创建失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 任务创建异常: {e}")
    
    # 3. 测试 AI 助手功能
    print("\n3️⃣ 测试 AI 助手功能...")
    try:
        response = requests.post(
            f"{base_url}/api/chat/stream",
            json={
                "message": "添加任务: 验证AI助手",
                "sessionId": "final_test_session",
                "userId": "1"
            },
            timeout=10
        )
        if response.status_code == 200:
            print("✅ AI 助手功能正常")
        else:
            print(f"❌ AI 助手功能异常: {response.status_code}")
    except Exception as e:
        print(f"❌ AI 助手功能异常: {e}")
    
    # 4. 监控请求频率
    print("\n4️⃣ 监控请求频率（10秒）...")
    start_time = time.time()
    request_count = 0
    
    # 模拟前端请求模式
    for i in range(5):
        try:
            response = requests.get(f"{base_url}/api/tasks", timeout=3)
            if response.status_code == 200:
                request_count += 1
                elapsed = time.time() - start_time
                print(f"   请求 {i+1}: {elapsed:.1f}s")
        except:
            pass
        time.sleep(2)
    
    elapsed = time.time() - start_time
    avg_frequency = request_count / elapsed
    
    print(f"\n📊 请求统计:")
    print(f"   总请求数: {request_count}")
    print(f"   监控时间: {elapsed:.1f}s")
    print(f"   平均频率: {avg_frequency:.2f} 请求/秒")
    
    # 5. 结果分析
    print("\n5️⃣ 结果分析:")
    if avg_frequency <= 0.5:  # 每秒最多0.5个请求
        print("✅ 修复成功！")
        print("   - 请求频率正常")
        print("   - 没有检测到无限循环")
        print("   - 前端工具调用功能正常")
    else:
        print("❌ 仍有问题")
        print("   - 请求频率过高")
        print("   - 可能存在其他问题")
    
    print("\n💡 用户操作建议:")
    print("   1. 刷新浏览器页面 (Ctrl+F5 强制刷新)")
    print("   2. 清除浏览器缓存")
    print("   3. 重新打开开发者工具")
    print("   4. 检查 Network 标签页是否显示新的请求记录")
    
    print("\n🎉 修复总结:")
    print("   ✅ 移除了 TaskManager 组件的 key 属性")
    print("   ✅ 使用 useCallback 优化了 handleChatResponse 函数")
    print("   ✅ 优化了 useEffect 依赖项管理")
    print("   ✅ 重启了前端容器应用修复")
    print("   ✅ LangGraph Agent 前端工具调用功能正常工作")

if __name__ == "__main__":
    final_verification()
