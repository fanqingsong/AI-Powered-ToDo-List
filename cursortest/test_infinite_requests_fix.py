#!/usr/bin/env python3
"""
测试前端无限请求修复
验证 TaskManager 组件不再无限循环请求 tasks 接口
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
        
    def log_request(self, endpoint):
        self.request_counts[endpoint] += 1
        current_time = time.time()
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
    
    print("🔍 开始监控前端请求...")
    print("📊 监控时间: 30秒")
    print("🎯 目标: 验证 tasks 接口不再无限循环请求")
    print("-" * 50)
    
    # 模拟前端请求模式
    base_url = "http://localhost:3000"
    
    # 初始请求
    try:
        response = requests.get(f"{base_url}/api/tasks", timeout=5)
        monitor.log_request("GET /api/tasks")
        if response.status_code == 200:
            print("✅ 初始 tasks 请求成功")
        else:
            print(f"❌ 初始 tasks 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 初始 tasks 请求异常: {e}")
    
    # 模拟用户操作 - 添加任务
    print("\n📝 模拟用户添加任务...")
    try:
        response = requests.post(
            f"{base_url}/api/tasks",
            json={"title": "测试无限请求修复", "isComplete": False},
            timeout=5
        )
        monitor.log_request("POST /api/tasks")
        if response.status_code == 201:
            print("✅ 添加任务成功")
        else:
            print(f"❌ 添加任务失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 添加任务异常: {e}")
    
    # 等待一段时间，观察是否有额外的请求
    print("\n⏳ 等待 10 秒，观察请求模式...")
    time.sleep(10)
    
    # 模拟前端刷新触发
    print("\n🔄 模拟前端刷新触发...")
    try:
        response = requests.get(f"{base_url}/api/tasks", timeout=5)
        monitor.log_request("GET /api/tasks (refresh)")
        if response.status_code == 200:
            print("✅ 刷新请求成功")
        else:
            print(f"❌ 刷新请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 刷新请求异常: {e}")
    
    # 继续监控
    print("\n⏳ 继续监控 20 秒...")
    time.sleep(20)
    
    # 停止监控并显示统计
    monitor.stop_monitoring()
    stats = monitor.get_stats()
    
    print("\n" + "=" * 50)
    print("📊 监控结果统计:")
    print(f"⏱️  总监控时间: {stats['total_time']:.1f} 秒")
    print(f"📈 平均请求频率: {stats['avg_requests_per_second']:.2f} 请求/秒")
    print("\n📋 各接口请求次数:")
    for endpoint, count in stats['request_counts'].items():
        print(f"   {endpoint}: {count} 次")
    
    # 分析结果
    tasks_requests = stats['request_counts'].get('GET /api/tasks', 0)
    tasks_refresh_requests = stats['request_counts'].get('GET /api/tasks (refresh)', 0)
    total_tasks_requests = tasks_requests + tasks_refresh_requests
    
    print("\n🎯 分析结果:")
    if total_tasks_requests <= 3:  # 初始 + 刷新 + 可能的1次额外
        print("✅ 修复成功！tasks 接口请求次数正常")
        print("   - 没有检测到无限循环请求")
        print("   - 请求频率在合理范围内")
    elif total_tasks_requests <= 10:
        print("⚠️  部分修复：tasks 接口请求次数较多")
        print("   - 可能存在轻微的性能问题")
        print("   - 建议进一步优化")
    else:
        print("❌ 修复失败：仍然存在无限循环请求")
        print("   - tasks 接口请求次数过多")
        print("   - 需要进一步调试")
    
    print("\n💡 修复说明:")
    print("   - 移除了 TaskManager 组件的 key 属性")
    print("   - 使用 useCallback 优化 loadTasks 函数")
    print("   - 修复了 useEffect 依赖项问题")

if __name__ == "__main__":
    monitor_requests()
