#!/usr/bin/env python3
"""
数据迁移脚本：将SQLite任务数据迁移到PostgreSQL
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.src.services.task_service import TaskService


async def main():
    """主迁移函数"""
    print("开始迁移任务数据从SQLite到PostgreSQL...")
    
    task_service = TaskService()
    
    try:
        # 执行迁移
        migrated_count = await task_service.migrate_from_sqlite()
        
        if migrated_count > 0:
            print(f"✅ 成功迁移 {migrated_count} 个任务")
            
            # 验证迁移结果
            tasks = await task_service.get_all_tasks()
            print(f"📊 PostgreSQL中现在有 {len(tasks)} 个任务")
            
            # 显示迁移的任务
            print("\n迁移的任务列表:")
            for task in tasks:
                status = "✅ 已完成" if task.isComplete else "⏳ 进行中"
                print(f"  - [{task.id}] {task.title} {status}")
        else:
            print("ℹ️  没有需要迁移的任务，或者任务已经存在")
            
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return 1
    
    print("\n🎉 迁移完成！")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
