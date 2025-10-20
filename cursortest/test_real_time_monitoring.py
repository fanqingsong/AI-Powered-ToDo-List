#!/usr/bin/env python3
"""
实时监控前端请求问题
检测是否还有无限循环请求 tasks 接口
"""

import time
import requests
import threading
from collections import defaultdict

class RequestMonitor:
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.start_time = time.time()
        self.monitoring = True
        self.last_request_time = {}
        
    def log_request(self, endpoint):
        current_time = time.time()
        self.request_counts[endpoint] += 1
        
        # 检查请求频率
        if endpoint in self.last_request_time:
            time_diff = current_time - self.last_request_time[endpoint]
            if time_diff < 1.0:  # 如果两次请求间隔小于1秒
                print(f"⚠️  高频请求警告: {endpoint} - 间隔 {time_diff:.2f}s")
        
        self.last_request_time[endpoint] = current_time
        
        elapsed = current_time - self.start_time
        print(f"[{elapsed:.1f}s] 请求 {endpoint} - 总计: {self.request_counts[endpoint]}")
        
    def stop_monitoring(self):
        self.monitoring = False
        
    def get_stats(self):
        total_time = time.time() - self.start_time
        return {
            'total_time': total_time,
            'request_counts': dict(self.request_counts),
            'avg_requests_per_second': sum(self.request_counts.values()) / total_time if total_time > 0 else 0
        }

def monitor_requests():
    """监控请求频率"""
    monitor = RequestMonitor()
    
    print("🔍 开始实时监控前端请求...")
    print("📊 监控时间: 60秒")
    print("🎯 目标: 检测无限循环请求问题")
    print("⚠️  如果看到高频请求警告，说明仍有问题")
    print("-" * 60)
    
    base_url = "http://localhost:3000"
    
    # 初始请求
    try:
        response = requests.get(f"{base_url}/api/tasks", timeout=5)
        monitor.log_request("GET /api/tasks (initial)")
        if response.status_code == 200:
            print("✅ 初始 tasks 请求成功")
        else:
            print(f"❌ 初始 tasks 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 初始 tasks 请求异常: {e}")
    
    # 模拟用户操作
    print("\n📝 模拟用户添加任务...")
    try:
        response = requests.post(
            f"{base_url}/api/tasks",
            json={"title": "测试无限请求修复2", "isComplete": False},
            timeout=5
        )
        monitor.log_request("POST /api/tasks")
        if response.status_code == 201:
            print("✅ 添加任务成功")
        else:
            print(f"❌ 添加任务失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 添加任务异常: {e}")
    
    # 等待并观察请求模式
    print("\n⏳ 等待 30 秒，观察请求模式...")
    time.sleep(30)
    
    # 模拟 AI 助手响应（包含刷新指令）
    print("\n🤖 模拟 AI 助手响应（包含刷新指令）...")
    try:
        response = requests.post(
            f"{base_url}/api/chat/stream",
            json={
                "message": "添加任务: 测试刷新",
                "sessionId": "test_session_monitor",
                "userId": "1"
            },
            timeout=10
        )
        monitor.log_request("POST /api/chat/stream")
        if response.status_code == 200:
            print("✅ AI 助手请求成功")
        else:
            print(f"❌ AI 助手请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ AI 助手请求异常: {e}")
    
    # 继续监控
    print("\n⏳ 继续监控 30 秒...")
    time.sleep(30)
    
    # 停止监控并显示统计
    monitor.stop_monitoring()
    stats = monitor.get_stats()
    
    print("\n" + "=" * 60)
    print("📊 监控结果统计:")
    print(f"⏱️  总监控时间: {stats['total_time']:.1f} 秒")
    print(f"📈 平均请求频率: {stats['avg_requests_per_second']:.2f} 请求/秒")
    print("\n📋 各接口请求次数:")
    for endpoint, count in stats['request_counts'].items():
        print(f"   {endpoint}: {count} 次")
    
    # 分析结果
    tasks_requests = stats['request_counts'].get('GET /api/tasks (initial)', 0)
    total_requests = sum(stats['request_counts'].values())
    
    print("\n🎯 分析结果:")
    if total_requests <= 5:  # 初始 + AI助手 + 可能的几次额外请求
        print("✅ 修复成功！请求次数正常")
        print("   - 没有检测到无限循环请求")
        print("   - 请求频率在合理范围内")
    elif total_requests <= 20:
        print("⚠️  部分修复：请求次数较多")
        print("   - 可能存在轻微的性能问题")
        print("   - 建议进一步优化")
    else:
        print("❌ 修复失败：仍然存在无限循环请求")
        print("   - 请求次数过多")
        print("   - 需要进一步调试")
    
    print("\n💡 修复措施:")
    print("   - 使用 useCallback 优化 handleChatResponse 函数")
    print("   - 移除 TaskManager 组件的 key 属性")
    print("   - 优化 useEffect 依赖项管理")
    print("   - 重启前端容器应用修复")

if __name__ == "__main__":
    monitor_requests()
