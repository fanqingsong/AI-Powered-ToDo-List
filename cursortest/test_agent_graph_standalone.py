"""
Agent Graph Builder 独立测试脚本

直接测试 agent.py 文件，不通过 src 包导入
"""

import sys
import os

# 直接添加 agent.py 的路径
agent_graph_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
sys.path.insert(0, agent_graph_path)

def test_direct_import():
    """直接导入 agent_graph 模块"""
    try:
        import agent_graph
        print("✓ agent_graph 模块导入成功")
        
        # 测试类定义
        from agent_graph import AgentGraphBuilder, FrontendTool, AnyArgsSchema
        print("✓ 类定义导入成功")
        
        # 测试 AnyArgsSchema
        schema = AnyArgsSchema()
        print("✓ AnyArgsSchema 创建成功")
        
        # 测试 FrontendTool
        tool = FrontendTool("test_tool")
        print("✓ FrontendTool 创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 直接导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_graph_builder():
    """测试图构建器"""
    try:
        import agent_graph
        
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
        builder = agent_graph.AgentGraphBuilder(llm, task_tools)
        print("✓ AgentGraphBuilder 创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 图构建器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("开始独立测试 AgentGraphBuilder...")
    print("=" * 50)
    
    tests = [
        ("直接导入", test_direct_import),
        ("图构建器", test_graph_builder),
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
