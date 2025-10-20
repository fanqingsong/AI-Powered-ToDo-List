"""
测试 agent_wrapper.py 重命名后的导入功能
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

def test_import():
    """测试导入功能"""
    try:
        # 直接导入 agent_wrapper 模块
        from agents.agent_wrapper import TaskManagementAgent
        print("✓ TaskManagementAgent 从 agent_wrapper 导入成功")
        
        # 通过 __init__.py 导入
        from agents import TaskAgent
        print("✓ TaskAgent 通过 __init__.py 导入成功")
        
        # 验证它们是同一个类
        assert TaskAgent is TaskManagementAgent
        print("✓ TaskAgent 和 TaskManagementAgent 是同一个类")
        
        return True
    except Exception as e:
        print(f"❌ 导入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_class_definition():
    """测试类定义"""
    try:
        from agents.agent_wrapper import TaskManagementAgent
        
        # 检查类的基本属性
        assert hasattr(TaskManagementAgent, '__init__')
        assert hasattr(TaskManagementAgent, 'process_message_stream')
        assert hasattr(TaskManagementAgent, 'set_user_id')
        print("✓ TaskManagementAgent 类定义完整")
        
        return True
    except Exception as e:
        print(f"❌ 类定义测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试 agent_wrapper.py 重命名后的功能...")
    print("=" * 60)
    
    tests = [
        ("导入功能", test_import),
        ("类定义", test_class_definition),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n测试: {test_name}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！agent_wrapper.py 重命名成功。")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
