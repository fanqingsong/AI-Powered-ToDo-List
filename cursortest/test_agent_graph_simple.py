"""
Agent Graph Builder 简单测试脚本

测试 agent.py 模块的基本功能，不依赖外部服务
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_import():
    """测试模块导入"""
    try:
        from src.agents.agent_graph import AgentGraphBuilder, create_agent_graph_builder, FrontendTool, AnyArgsSchema
        print("✓ 模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_classes():
    """测试类定义"""
    try:
        from src.agents.agent_graph import AgentGraphBuilder, FrontendTool, AnyArgsSchema
        
        # 测试 AnyArgsSchema
        schema = AnyArgsSchema()
        print("✓ AnyArgsSchema 创建成功")
        
        # 测试 FrontendTool
        tool = FrontendTool("test_tool")
        print("✓ FrontendTool 创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 类测试失败: {e}")
        return False

def test_graph_builder_creation():
    """测试图构建器创建（不依赖外部服务）"""
    try:
        from src.agents.agent_graph import AgentGraphBuilder
        
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
        
        # 创建图构建器
        llm = MockLLM()
        task_tools = MockTaskTools()
        builder = AgentGraphBuilder(llm, task_tools)
        print("✓ AgentGraphBuilder 创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 图构建器创建失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试 AgentGraphBuilder...")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_import),
        ("类定义", test_classes),
        ("图构建器创建", test_graph_builder_creation),
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
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！AgentGraphBuilder 基本功能正常。")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
