"""
测试重构后的图构建器功能

验证新的继承架构是否正常工作
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

def test_imports():
    """测试所有新模块的导入"""
    try:
        from agents.base_agent_graph import BaseAgentGraph, AnyArgsSchema, FrontendTool
        print("✓ BaseAgentGraph 导入成功")
        
        from agents.assistant_ui_graph import AssistantUIGraph, create_assistant_ui_graph
        print("✓ AssistantUIGraph 导入成功")
        
        from agents.standard_graph import StandardGraph, create_standard_graph
        print("✓ StandardGraph 导入成功")
        
        from agents.custom_graph import CustomGraph, create_custom_graph
        print("✓ CustomGraph 导入成功")
        
        from agents.graph_builder_factory import GraphBuilderFactory, create_graph_builder_factory
        print("✓ GraphBuilderFactory 导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_class_hierarchy():
    """测试类继承关系"""
    try:
        from agents.base_agent_graph import BaseAgentGraph
        from agents.assistant_ui_graph import AssistantUIGraph
        from agents.standard_graph import StandardGraph
        from agents.custom_graph import CustomGraph
        
        # 检查继承关系
        assert issubclass(AssistantUIGraph, BaseAgentGraph)
        print("✓ AssistantUIGraph 继承自 BaseAgentGraph")
        
        assert issubclass(StandardGraph, BaseAgentGraph)
        print("✓ StandardGraph 继承自 BaseAgentGraph")
        
        assert issubclass(CustomGraph, BaseAgentGraph)
        print("✓ CustomGraph 继承自 BaseAgentGraph")
        
        return True
    except Exception as e:
        print(f"❌ 类继承测试失败: {e}")
        return False

def test_graph_creation():
    """测试图创建功能"""
    try:
        from agents.graph_builder_factory import create_graph_builder_factory
        
        # 创建模拟的 LLM 和 TaskTools
        class MockLLM:
            def bind_tools(self, tools):
                return self
        
            async def ainvoke(self, messages):
                return {"content": "test response"}
        
        class MockTaskTools:
            def get_tool_definitions(self):
                return []
            
            def get_tools(self):
                return []
        
        # 创建图构建器工厂
        llm = MockLLM()
        task_tools = MockTaskTools()
        factory = create_graph_builder_factory(llm, task_tools)
        print("✓ GraphBuilderFactory 创建成功")
        
        # 测试创建不同类型的图
        assistant_ui_graph = factory.create_assistant_ui_graph()
        print("✓ AssistantUIGraph 创建成功")
        
        standard_graph = factory.create_standard_graph()
        print("✓ StandardGraph 创建成功")
        
        custom_graph = factory.create_custom_graph()
        print("✓ CustomGraph 创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 图创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_wrapper_integration():
    """测试 agent_wrapper.py 的集成"""
    try:
        # 检查 agent_wrapper.py 的导入
        with open(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents', 'agent_wrapper.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否使用了新的导入
        assert 'from .graph_builder_factory import create_graph_builder_factory' in content
        print("✓ agent_wrapper.py 使用了新的图构建器工厂")
        
        assert 'self.graph_builder_factory = create_graph_builder_factory(self.llm, self.task_tools)' in content
        print("✓ agent_wrapper.py 正确初始化了图构建器工厂")
        
        # 检查是否移除了旧的导入
        assert 'from .agent import create_agent_graph_builder' not in content
        print("✓ agent_wrapper.py 移除了旧的导入")
        
        return True
    except Exception as e:
        print(f"❌ agent_wrapper 集成测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试重构后的图构建器功能...")
    print("=" * 60)
    
    tests = [
        ("模块导入", test_imports),
        ("类继承关系", test_class_hierarchy),
        ("图创建功能", test_graph_creation),
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
        print("🎉 所有测试通过！重构成功完成。")
        print("\n重构总结:")
        print("- ✅ 创建了 BaseAgentGraph 基础类")
        print("- ✅ 创建了 AssistantUIGraph 专用类")
        print("- ✅ 创建了 StandardGraph 标准类")
        print("- ✅ 创建了 CustomGraph 自定义类")
        print("- ✅ 创建了 GraphBuilderFactory 工厂类")
        print("- ✅ 更新了 agent_wrapper.py 使用新的架构")
        print("- ✅ 使用继承思想封装了公共逻辑")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
