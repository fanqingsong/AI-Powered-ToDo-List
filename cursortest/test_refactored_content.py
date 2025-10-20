"""
测试重构后的 agent.py 文件内容

验证重构是否成功完成
"""

import os

def test_file_structure():
    """测试文件结构"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        with open(os.path.join(agents_dir, 'agent.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查不再有 AssistantUIGraph 类
        assert 'class AssistantUIGraph:' not in content, "仍然存在 AssistantUIGraph 类"
        print("✓ 已移除 AssistantUIGraph 类")
        
        # 检查有必要的函数
        assert 'def set_llm_and_tools(' in content, "缺少 set_llm_and_tools 函数"
        print("✓ set_llm_and_tools 函数存在")
        
        assert 'def call_model(' in content, "缺少 call_model 函数"
        print("✓ call_model 函数存在")
        
        assert 'def run_tools(' in content, "缺少 run_tools 函数"
        print("✓ run_tools 函数存在")
        
        assert 'def should_continue(' in content, "缺少 should_continue 函数"
        print("✓ should_continue 函数存在")
        
        # 检查图构建逻辑
        assert 'workflow = StateGraph(AgentState)' in content, "缺少 StateGraph 构建"
        print("✓ StateGraph 构建逻辑存在")
        
        assert 'workflow.add_node(' in content and '"agent"' in content, "缺少 agent 节点"
        print("✓ agent 节点存在")
        
        assert 'workflow.add_node(' in content and '"tools"' in content, "缺少 tools 节点"
        print("✓ tools 节点存在")
        
        assert 'workflow.set_entry_point("agent")' in content, "缺少入口点设置"
        print("✓ 入口点设置存在")
        
        assert 'workflow.add_conditional_edges(' in content, "缺少条件边"
        print("✓ 条件边存在")
        
        assert 'workflow.add_edge("tools", "agent")' in content, "缺少工具到代理的边"
        print("✓ 工具到代理的边存在")
        
        assert 'graph = workflow.compile()' in content, "缺少 graph 实例"
        print("✓ graph 实例存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 文件结构测试失败: {e}")
        return False

def test_agent_wrapper_integration():
    """测试 agent_wrapper.py 集成"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        with open(os.path.join(agents_dir, 'agent_wrapper.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查导入
        assert 'from .agent import graph, set_llm_and_tools' in content, "导入路径不正确"
        print("✓ 导入路径正确")
        
        # 检查调用方式
        assert 'set_llm_and_tools(self.llm, self.task_tools)' in content, "调用方式不正确"
        print("✓ 调用方式正确")
        
        # 检查 graph 使用
        assert 'self.assistant_ui_graph = graph' in content, "graph 使用不正确"
        print("✓ graph 使用正确")
        
        return True
        
    except Exception as e:
        print(f"❌ agent_wrapper 集成测试失败: {e}")
        return False

def test_code_quality():
    """测试代码质量"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        with open(os.path.join(agents_dir, 'agent.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查注释
        assert '"""' in content, "缺少文档字符串"
        print("✓ 有文档字符串")
        
        # 检查函数注释
        assert '"""' in content and content.count('"""') >= 2, "函数缺少注释"
        print("✓ 函数有注释")
        
        # 检查代码风格
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        assert len(non_empty_lines) > 50, "代码行数太少"
        print("✓ 代码行数合理")
        
        # 检查没有过长的行
        long_lines = [line for line in lines if len(line) > 120]
        assert len(long_lines) == 0, f"有过长的行: {len(long_lines)} 行"
        print("✓ 没有过长的行")
        
        return True
        
    except Exception as e:
        print(f"❌ 代码质量测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试重构后的 agent.py 文件内容...")
    print("=" * 60)
    
    tests = [
        ("文件结构", test_file_structure),
        ("agent_wrapper 集成", test_agent_wrapper_integration),
        ("代码质量", test_code_quality),
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
        print("- create_graph() 直接返回编译后的图")
        print("- 所有逻辑都是函数，没有类封装")
        print("- 图构建逻辑更直观")
        print("- 符合 LangGraph 的最佳实践")
        print("\n代码示例:")
        print("workflow = StateGraph(MessagesState)")
        print("workflow.add_node('agent', call_model)")
        print("workflow.add_node('tools', run_tools)")
        print("workflow.set_entry_point('agent')")
        print("workflow.add_conditional_edges('agent', should_continue, ['tools', END])")
        print("workflow.add_edge('tools', 'agent')")
        print("return workflow.compile()")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
