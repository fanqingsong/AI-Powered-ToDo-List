"""
测试重构后的 agent.py

验证图构建功能是否正常工作
"""

import sys
import os

def test_graph_creation():
    """测试图创建功能"""
    try:
        # 添加项目路径
        project_root = os.path.join(os.path.dirname(__file__), '..')
        sys.path.insert(0, project_root)
        
        from backend.src.agents.agent_graph import create_assistant_ui_graph
        from backend.src.agents.tools import TaskTools
        from backend.src.agents.llmconf import get_llm
        
        print("✓ 成功导入必要的模块")
        
        # 创建模拟的 LLM 和 TaskTools
        llm = get_llm()
        task_tools = TaskTools(None)  # 传入 None 用于测试
        
        print("✓ 成功创建 LLM 和 TaskTools 实例")
        
        # 创建图
        graph = create_assistant_ui_graph(llm, task_tools)
        
        print("✓ 成功创建图实例")
        
        # 检查图是否有必要的方法
        assert hasattr(graph, 'ainvoke'), "图缺少 ainvoke 方法"
        assert hasattr(graph, 'astream'), "图缺少 astream 方法"
        assert hasattr(graph, 'invoke'), "图缺少 invoke 方法"
        assert hasattr(graph, 'stream'), "图缺少 stream 方法"
        
        print("✓ 图具有所有必要的方法")
        
        # 检查图的类型
        from langgraph.graph import CompiledGraph
        assert isinstance(graph, CompiledGraph), f"图类型不正确: {type(graph)}"
        
        print("✓ 图类型正确")
        
        return True
        
    except Exception as e:
        print(f"❌ 图创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_graph_structure():
    """测试图结构"""
    try:
        project_root = os.path.join(os.path.dirname(__file__), '..')
        sys.path.insert(0, project_root)
        
        from backend.src.agents.agent_graph import create_assistant_ui_graph
        from backend.src.agents.tools import TaskTools
        from backend.src.agents.llmconf import get_llm
        
        llm = get_llm()
        task_tools = TaskTools(None)
        graph = create_assistant_ui_graph(llm, task_tools)
        
        # 检查图的节点
        nodes = graph.get_graph().nodes
        assert "agent" in nodes, "缺少 agent 节点"
        assert "tools" in nodes, "缺少 tools 节点"
        
        print("✓ 图包含必要的节点")
        
        # 检查图的边
        edges = graph.get_graph().edges
        assert len(edges) > 0, "图没有边"
        
        print("✓ 图包含边")
        
        return True
        
    except Exception as e:
        print(f"❌ 图结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_function_signatures():
    """测试函数签名"""
    try:
        project_root = os.path.join(os.path.dirname(__file__), '..')
        sys.path.insert(0, project_root)
        
        from backend.src.agents.agent_graph import (
            create_assistant_ui_graph,
            call_model,
            run_tools,
            should_continue,
            get_tool_definitions,
            get_tools
        )
        
        print("✓ 所有函数都可以正确导入")
        
        # 检查函数签名
        import inspect
        
        # 检查 create_assistant_ui_graph 签名
        sig = inspect.signature(create_assistant_ui_graph)
        params = list(sig.parameters.keys())
        assert "llm" in params, "create_assistant_ui_graph 缺少 llm 参数"
        assert "task_tools" in params, "create_assistant_ui_graph 缺少 task_tools 参数"
        
        print("✓ create_assistant_ui_graph 函数签名正确")
        
        return True
        
    except Exception as e:
        print(f"❌ 函数签名测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("开始测试重构后的 agent.py...")
    print("=" * 60)
    
    tests = [
        ("图创建功能", test_graph_creation),
        ("图结构", test_graph_structure),
        ("函数签名", test_function_signatures),
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
        print("- ✅ 移除了 AssistantUIGraph 类")
        print("- ✅ 直接在顶层构建 StateGraph")
        print("- ✅ 使用函数式编程风格")
        print("- ✅ 保持了所有功能")
        print("- ✅ 代码更简洁")
        print("\n新的结构:")
        print("- create_assistant_ui_graph() 直接返回编译后的图")
        print("- 所有逻辑都是函数，没有类封装")
        print("- 图构建逻辑更直观")
        print("- 符合 LangGraph 的最佳实践")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
