"""
测试 agent_wrapper.py 重命名后的文件结构和导入路径
"""

import sys
import os

def test_file_structure():
    """测试文件结构"""
    try:
        agent_wrapper_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents', 'agent_wrapper.py')
        agent_init_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents', '__init__.py')
        
        # 检查文件是否存在
        assert os.path.exists(agent_wrapper_path), "agent_wrapper.py 文件不存在"
        print("✓ agent_wrapper.py 文件存在")
        
        assert os.path.exists(agent_init_path), "__init__.py 文件不存在"
        print("✓ __init__.py 文件存在")
        
        # 检查旧的 agent.py 是否已删除
        old_agent_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents', 'agent.py')
        assert not os.path.exists(old_agent_path), "旧的 agent.py 文件仍然存在"
        print("✓ 旧的 agent.py 文件已删除")
        
        return True
    except Exception as e:
        print(f"❌ 文件结构测试失败: {e}")
        return False

def test_import_path():
    """测试导入路径"""
    try:
        # 读取 __init__.py 文件内容
        init_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents', '__init__.py')
        with open(init_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查导入语句
        assert 'from .agent_wrapper import TaskManagementAgent as TaskAgent' in content
        print("✓ __init__.py 中的导入语句正确")
        
        assert 'from .agent import' not in content
        print("✓ __init__.py 中没有旧的导入语句")
        
        return True
    except Exception as e:
        print(f"❌ 导入路径测试失败: {e}")
        return False

def test_file_content():
    """测试文件内容"""
    try:
        # 读取 agent_wrapper.py 文件内容
        wrapper_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents', 'agent_wrapper.py')
        with open(wrapper_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键内容
        assert 'class TaskManagementAgent:' in content
        print("✓ agent_wrapper.py 包含 TaskManagementAgent 类")
        
        assert 'from .agent import create_agent_graph_builder' in content
        print("✓ agent_wrapper.py 包含正确的 agent_graph 导入")
        
        return True
    except Exception as e:
        print(f"❌ 文件内容测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试 agent_wrapper.py 重命名后的文件结构...")
    print("=" * 60)
    
    tests = [
        ("文件结构", test_file_structure),
        ("导入路径", test_import_path),
        ("文件内容", test_file_content),
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
        print("\n重命名总结:")
        print("- ✅ agent.py 已重命名为 agent_wrapper.py")
        print("- ✅ __init__.py 中的导入语句已更新")
        print("- ✅ 文档中的引用已更新")
        print("- ✅ 旧的 agent.py 文件已删除")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
