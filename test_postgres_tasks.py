#!/usr/bin/env python3
"""
测试PostgreSQL任务存储功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.src.services.task_service import TaskService


async def test_task_service():
    """测试任务服务功能"""
    print("🧪 开始测试PostgreSQL任务存储...")
    
    task_service = TaskService()
    
    try:
        # 测试1: 添加任务
        print("\n1️⃣ 测试添加任务...")
        task1 = await task_service.add_task("测试任务1", False)
        task2 = await task_service.add_task("测试任务2", True)
        print(f"✅ 添加任务成功: {task1.title} (ID: {task1.id})")
        print(f"✅ 添加任务成功: {task2.title} (ID: {task2.id})")
        
        # 测试2: 获取所有任务
        print("\n2️⃣ 测试获取所有任务...")
        all_tasks = await task_service.get_all_tasks()
        print(f"✅ 获取到 {len(all_tasks)} 个任务:")
        for task in all_tasks:
            status = "✅ 已完成" if task.isComplete else "⏳ 进行中"
            print(f"  - [{task.id}] {task.title} {status}")
        
        # 测试3: 根据ID获取任务
        print("\n3️⃣ 测试根据ID获取任务...")
        task_by_id = await task_service.get_task_by_id(task1.id)
        if task_by_id:
            print(f"✅ 根据ID获取任务成功: {task_by_id.title}")
        else:
            print("❌ 根据ID获取任务失败")
        
        # 测试4: 更新任务
        print("\n4️⃣ 测试更新任务...")
        updated = await task_service.update_task(task1.id, "更新后的测试任务1", True)
        if updated:
            updated_task = await task_service.get_task_by_id(task1.id)
            print(f"✅ 更新任务成功: {updated_task.title} (完成状态: {updated_task.isComplete})")
        else:
            print("❌ 更新任务失败")
        
        # 测试5: 获取任务统计
        print("\n5️⃣ 测试任务统计...")
        total_count = await task_service.get_task_count()
        completed_count = await task_service.get_completed_task_count()
        print(f"✅ 总任务数: {total_count}")
        print(f"✅ 已完成任务数: {completed_count}")
        
        # 测试6: 删除任务
        print("\n6️⃣ 测试删除任务...")
        deleted = await task_service.delete_task(task2.id)
        if deleted:
            print(f"✅ 删除任务成功 (ID: {task2.id})")
        else:
            print("❌ 删除任务失败")
        
        # 最终验证
        print("\n🔍 最终验证...")
        final_tasks = await task_service.get_all_tasks()
        print(f"✅ 最终任务数量: {len(final_tasks)}")
        
        print("\n🎉 所有测试通过！PostgreSQL任务存储功能正常")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    success = await test_task_service()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
