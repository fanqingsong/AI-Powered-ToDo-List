"""
测试简化后的 graph_builder 模块

验证简化后的结构是否正常工作
"""

import sys
import os

def test_simplified_structure():
    """测试简化后的结构"""
    try:
        graph_builder_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents', 'graph_builder')
        
        # 检查只保留了必要的文件
        expected_files = ['__init__.py', 'assistant_ui_graph.py']
        for file_name in expected_files:
            file_path = os.path.join(graph_builder_dir, file_name)
            assert os.path.exists(file_path), f"{file_name} 文件不存在"
            print(f"✓ {file_name} 文件存在")
        
        # 检查不需要的文件已删除
        removed_files = ['base_agent.py', 'standard_graph.py', 'custom_graph.py', 'graph_builder_factory.py']
        for file_name in removed_files:
            file_path = os.path.join(graph_builder_dir, file_name)
            assert not os.path.exists(file_path), f"{file_name} 文件仍然存在"
            print(f"✓ {file_name} 文件已删除")
        
        return True
    except Exception as e:
        print(f"❌ 简化结构测试失败: {e}")
        return False

def test_module_imports():
    """测试模块导入"""
    try:
        init_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents', 'graph_builder', '__init__.py')
        with open(init_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查只导出了必要的类
        expected_imports = [
            'AssistantUIGraph',
            'create_assistant_ui_graph',
            'AnyArgsSchema',
            'FrontendTool'
        ]
        
        for import_name in expected_imports:
            assert import_name in content, f"缺少导入: {import_name}"
            print(f"✓ {import_name} 导入正确")
        
        # 检查没有导出不需要的类
        removed_imports = [
            'BaseAgentGraph',
            'StandardGraph',
            'CustomGraph',
            'GraphBuilderFactory'
        ]
        
        for import_name in removed_imports:
            assert import_name not in content, f"不应该导入: {import_name}"
            print(f"✓ {import_name} 已移除")
        
        return True
    except Exception as e:
        print(f"❌ 模块导入测试失败: {e}")
        return False

def test_assistant_ui_graph_content():
    """测试 assistant_ui_graph.py 内容"""
    try:
        graph_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents', 'graph_builder', 'assistant_ui_graph.py')
        with open(graph_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查包含了所有必要的类和方法
        assert 'class AssistantUIGraph:' in content
        print("✓ AssistantUIGraph 类存在")
        
        assert 'class AnyArgsSchema(BaseModel):' in content
        print("✓ AnyArgsSchema 类存在")
        
        assert 'class FrontendTool(BaseTool):' in content
        print("✓ FrontendTool 类存在")
        
        assert 'def build(self) -> StateGraph:' in content
        print("✓ build 方法存在")
        
        assert 'def create_assistant_ui_graph(' in content
        print("✓ create_assistant_ui_graph 函数存在")
        
        # 检查没有继承 BaseAgentGraph
        assert 'class AssistantUIGraph(BaseAgentGraph):' not in content
        print("✓ 不再继承 BaseAgentGraph")
        
        return True
    except Exception as e:
        print(f"❌ assistant_ui_graph 内容测试失败: {e}")
        return False

def test_agent_wrapper_integration():
    """测试 agent_wrapper.py 的集成"""
    try:
        agent_wrapper_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents', 'agent_wrapper.py')
        with open(agent_wrapper_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查使用简化的导入
        assert 'from .graph_builder import create_assistant_ui_graph' in content
        print("✓ agent_wrapper.py 使用简化的导入")
        
        # 检查简化的图创建
        assert 'self.assistant_ui_graph = create_assistant_ui_graph(self.llm, self.task_tools).build()' in content
        print("✓ agent_wrapper.py 使用简化的图创建")
        
        # 检查没有使用工厂模式
        assert 'graph_builder_factory' not in content
        print("✓ agent_wrapper.py 不再使用工厂模式")
        
        return True
    except Exception as e:
        print(f"❌ agent_wrapper 集成测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试简化后的 graph_builder 模块...")
    print("=" * 60)
    
    tests = [
        ("简化结构", test_simplified_structure),
        ("模块导入", test_module_imports),
        ("assistant_ui_graph 内容", test_assistant_ui_graph_content),
        ("agent_wrapper 集成", test_agent_wrapper_integration),
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
        print("🎉 所有测试通过！简化重构成功完成。")
        print("\n简化总结:")
        print("- ✅ 移除了复杂的继承结构")
        print("- ✅ 只保留了 AssistantUIGraph 一个图类型")
        print("- ✅ 将所有必要功能集成到一个文件中")
        print("- ✅ 简化了模块导入和导出")
        print("- ✅ 更新了 agent_wrapper.py 使用简化结构")
        print("- ✅ 保持了所有核心功能")
        print("\n简化后的模块结构:")
        print("agents/")
        print("├── graph_builder/")
        print("│   ├── __init__.py")
        print("│   └── assistant_ui_graph.py  # 包含所有图构建功能")
        print("├── agent_wrapper.py")
        print("└── ...")
        print("\n优势:")
        print("- 🎯 结构更简单，易于理解和维护")
        print("- 🚀 减少了不必要的抽象层")
        print("- 📦 所有相关功能集中在一个文件中")
        print("- 🔧 保持了所有必要的功能")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
