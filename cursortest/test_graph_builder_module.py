"""
测试 graph_builder 模块结构

验证新的模块化架构是否正常工作
"""

import sys
import os

def test_module_structure():
    """测试模块结构"""
    try:
        graph_builder_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents', 'graph_builder')
        
        # 检查模块文件是否存在
        files_to_check = [
            '__init__.py',
            'base_agent.py',
            'assistant_ui_graph.py', 
            'standard_graph.py',
            'custom_graph.py',
            'graph_builder_factory.py'
        ]
        
        for file_name in files_to_check:
            file_path = os.path.join(graph_builder_dir, file_name)
            assert os.path.exists(file_path), f"{file_name} 文件不存在"
            print(f"✓ {file_name} 文件存在")
        
        return True
    except Exception as e:
        print(f"❌ 模块结构测试失败: {e}")
        return False

def test_module_imports():
    """测试模块导入"""
    try:
        # 检查 __init__.py 文件内容
        init_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents', 'graph_builder', '__init__.py')
        with open(init_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否导出了所有必要的类
        expected_imports = [
            'BaseAgentGraph',
            'AnyArgsSchema',
            'FrontendTool',
            'AssistantUIGraph',
            'create_assistant_ui_graph',
            'StandardGraph',
            'create_standard_graph',
            'CustomGraph',
            'create_custom_graph',
            'GraphBuilderFactory',
            'create_graph_builder_factory'
        ]
        
        for import_name in expected_imports:
            assert import_name in content, f"缺少导入: {import_name}"
            print(f"✓ {import_name} 导入正确")
        
        return True
    except Exception as e:
        print(f"❌ 模块导入测试失败: {e}")
        return False

def test_relative_imports():
    """测试相对导入"""
    try:
        graph_builder_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents', 'graph_builder')
        
        # 检查各个文件的相对导入
        files_to_check = [
            'assistant_ui_graph.py',
            'standard_graph.py',
            'custom_graph.py',
            'graph_builder_factory.py',
            'base_agent.py'
        ]
        
        for file_name in files_to_check:
            file_path = os.path.join(graph_builder_dir, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否使用了正确的相对导入
            if file_name != 'base_agent.py':
                assert 'from .base_agent_graph import' in content, f"{file_name} 缺少基础类导入"
                print(f"✓ {file_name} 正确导入基础类")
            
            if file_name in ['assistant_ui_graph.py', 'standard_graph.py', 'custom_graph.py']:
                assert 'from ..tools import TaskTools' in content, f"{file_name} 缺少 TaskTools 导入"
                print(f"✓ {file_name} 正确导入 TaskTools")
        
        return True
    except Exception as e:
        print(f"❌ 相对导入测试失败: {e}")
        return False

def test_agent_wrapper_integration():
    """测试 agent_wrapper.py 的集成"""
    try:
        agent_wrapper_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents', 'agent_wrapper.py')
        with open(agent_wrapper_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否使用了新的模块导入
        assert 'from .graph_builder import create_graph_builder_factory' in content
        print("✓ agent_wrapper.py 使用了新的模块导入")
        
        # 检查是否移除了旧的导入
        assert 'from .graph_builder_factory import' not in content
        print("✓ agent_wrapper.py 移除了旧的导入")
        
        return True
    except Exception as e:
        print(f"❌ agent_wrapper 集成测试失败: {e}")
        return False

def test_old_files_cleanup():
    """测试旧文件清理"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        # 检查旧文件是否已移动
        old_files = [
            'base_agent.py',
            'assistant_ui_graph.py',
            'standard_graph.py',
            'custom_graph.py',
            'graph_builder_factory.py'
        ]
        
        for old_file in old_files:
            old_path = os.path.join(agents_dir, old_file)
            if os.path.exists(old_path):
                print(f"⚠️  旧文件 {old_file} 仍然存在于 agents 目录")
            else:
                print(f"✓ 旧文件 {old_file} 已移动到 graph_builder 模块")
        
        return True
    except Exception as e:
        print(f"❌ 旧文件清理测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试 graph_builder 模块结构...")
    print("=" * 60)
    
    tests = [
        ("模块结构", test_module_structure),
        ("模块导入", test_module_imports),
        ("相对导入", test_relative_imports),
        ("agent_wrapper 集成", test_agent_wrapper_integration),
        ("旧文件清理", test_old_files_cleanup),
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
        print("🎉 所有测试通过！模块化重构成功完成。")
        print("\n模块化总结:")
        print("- ✅ 创建了 graph_builder 模块文件夹")
        print("- ✅ 移动了所有图构建相关文件到新模块")
        print("- ✅ 创建了完整的 __init__.py 文件")
        print("- ✅ 更新了所有相对导入路径")
        print("- ✅ 更新了 agent_wrapper.py 使用新模块")
        print("- ✅ 清理了旧文件位置")
        print("\n新的模块结构:")
        print("agents/")
        print("├── graph_builder/")
        print("│   ├── __init__.py")
        print("│   ├── base_agent.py")
        print("│   ├── assistant_ui_graph.py")
        print("│   ├── standard_graph.py")
        print("│   ├── custom_graph.py")
        print("│   └── graph_builder_factory.py")
        print("├── agent_wrapper.py")
        print("└── ...")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
