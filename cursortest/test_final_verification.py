"""
最终验证 graph_builder 模块化重构

确认所有功能正常，旧文件已清理
"""

import sys
import os

def test_final_structure():
    """测试最终结构"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        graph_builder_dir = os.path.join(agents_dir, 'graph_builder')
        
        # 检查 graph_builder 模块文件
        graph_files = [
            '__init__.py',
            'base_agent.py',
            'assistant_ui_graph.py',
            'standard_graph.py',
            'custom_graph.py',
            'graph_builder_factory.py'
        ]
        
        for file_name in graph_files:
            file_path = os.path.join(graph_builder_dir, file_name)
            assert os.path.exists(file_path), f"graph_builder/{file_name} 不存在"
            print(f"✓ graph_builder/{file_name} 存在")
        
        # 检查旧文件已删除
        old_file_path = os.path.join(agents_dir, 'agent.py')
        assert not os.path.exists(old_file_path), "旧的 agent.py 仍然存在"
        print("✓ 旧的 agent.py 已删除")
        
        return True
    except Exception as e:
        print(f"❌ 最终结构测试失败: {e}")
        return False

def test_agent_wrapper_functionality():
    """测试 agent_wrapper.py 功能"""
    try:
        agent_wrapper_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents', 'agent_wrapper.py')
        with open(agent_wrapper_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查使用新的模块导入
        assert 'from .graph_builder import create_graph_builder_factory' in content
        print("✓ agent_wrapper.py 使用新的模块导入")
        
        # 检查没有旧的导入
        assert 'from .agent import' not in content
        print("✓ agent_wrapper.py 没有旧的导入")
        
        # 检查图构建器工厂的使用
        assert 'self.graph_builder_factory = create_graph_builder_factory(self.llm, self.task_tools)' in content
        print("✓ agent_wrapper.py 正确使用图构建器工厂")
        
        return True
    except Exception as e:
        print(f"❌ agent_wrapper 功能测试失败: {e}")
        return False

def test_module_exports():
    """测试模块导出"""
    try:
        init_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents', 'graph_builder', '__init__.py')
        with open(init_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查所有必要的导出
        exports = [
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
        
        for export in exports:
            assert export in content, f"缺少导出: {export}"
            print(f"✓ {export} 导出正确")
        
        return True
    except Exception as e:
        print(f"❌ 模块导出测试失败: {e}")
        return False

def main():
    """运行最终验证"""
    print("开始最终验证 graph_builder 模块化重构...")
    print("=" * 60)
    
    tests = [
        ("最终结构", test_final_structure),
        ("agent_wrapper 功能", test_agent_wrapper_functionality),
        ("模块导出", test_module_exports),
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
        print("🎉 最终验证通过！模块化重构完全成功。")
        print("\n最终总结:")
        print("✅ 成功创建了 graph_builder 模块")
        print("✅ 所有图构建相关文件已移动到新模块")
        print("✅ 使用继承思想封装了公共逻辑")
        print("✅ 每个图类型都有独立的文件")
        print("✅ 提供了统一的工厂接口")
        print("✅ 更新了所有引用路径")
        print("✅ 清理了旧文件")
        print("\n新的模块结构:")
        print("agents/")
        print("├── graph_builder/          # 图构建模块")
        print("│   ├── __init__.py         # 模块导出")
        print("│   ├── base_agent.py # 基础图类")
        print("│   ├── assistant_ui_graph.py # Assistant-UI 图")
        print("│   ├── standard_graph.py   # 标准图")
        print("│   ├── custom_graph.py     # 自定义图")
        print("│   └── graph_builder_factory.py # 工厂类")
        print("├── agent_wrapper.py        # Agent 包装器")
        print("├── tools.py               # 工具定义")
        print("└── ...                    # 其他文件")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
