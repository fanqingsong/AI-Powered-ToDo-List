#!/usr/bin/env python3
"""
管理员账户初始化测试脚本
用于测试管理员账户的自动创建和检查功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from src.services.admin_init_service import admin_init_service


async def test_admin_initialization():
    """测试管理员账户初始化功能"""
    print("🧪 开始测试管理员账户初始化功能...")
    
    try:
        # 测试1: 检查管理员是否存在
        print("\n1️⃣ 检查管理员账户是否存在...")
        admin_exists = await admin_init_service.check_admin_exists()
        print(f"   结果: {'存在' if admin_exists else '不存在'}")
        
        # 测试2: 确保管理员存在
        print("\n2️⃣ 确保管理员账户存在...")
        success = await admin_init_service.ensure_admin_exists()
        print(f"   结果: {'成功' if success else '失败'}")
        
        # 测试3: 再次检查管理员是否存在
        print("\n3️⃣ 再次检查管理员账户是否存在...")
        admin_exists_after = await admin_init_service.check_admin_exists()
        print(f"   结果: {'存在' if admin_exists_after else '不存在'}")
        
        # 测试4: 数据库架构初始化
        print("\n4️⃣ 测试数据库架构初始化...")
        schema_ok = await admin_init_service.initialize_database_schema()
        print(f"   结果: {'成功' if schema_ok else '失败'}")
        
        print("\n✅ 所有测试完成！")
        
        if success and admin_exists_after:
            print("🎉 管理员账户初始化功能正常工作")
        else:
            print("❌ 管理员账户初始化功能存在问题")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_admin_initialization())
