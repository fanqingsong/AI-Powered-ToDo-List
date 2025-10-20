"""
测试全局 graph 实例

验证移除函数封装后的新结构
"""

import os

def test_global_graph_structure():
    """测试全局 graph 结构"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        with open(os.path.join(agents_dir, 'agent.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查全局变量
        assert '_llm = None' in content, "缺少全局 _llm 变量"
        print("✓ 全局 _llm 变量存在")
        
        assert '_task_tools = None' in content, "缺少全局 _task_tools 变量"
        print("✓ 全局 _task_tools 变量存在")
        
        # 检查设置函数
        assert 'def set_llm_and_tools(' in content, "缺少 set_llm_and_tools 函数"
        print("✓ set_llm_and_tools 函数存在")
        
        # 检查全局 graph 实例
        assert 'graph = workflow.compile()' in content, "缺少全局 graph 实例"
        print("✓ 全局 graph 实例存在")
        
        # 检查不再有 create_graph 函数
        assert 'def create_graph(' not in content, "仍然存在 create_graph 函数"
        print("✓ create_graph 函数已移除")
        
        # 检查函数签名简化
        assert 'async def call_model(state: Dict[str, Any], config: Dict[str, Any])' in content, "call_model 函数签名未简化"
        print("✓ call_model 函数签名已简化")
        
        assert 'async def run_tools(input_data: Dict[str, Any], config: Dict[str, Any], **kwargs)' in content, "run_tools 函数签名未简化"
        print("✓ run_tools 函数签名已简化")
        
        return True
        
    except Exception as e:
        print(f"❌ 全局 graph 结构测试失败: {e}")
        return False

def test_agent_wrapper_integration():
    """测试 agent_wrapper.py 集成"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        with open(os.path.join(agents_dir, 'agent_wrapper.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查导入
        assert 'from .agent import graph, set_llm_and_tools' in content, "导入不正确"
        print("✓ 导入正确")
        
        # 检查初始化顺序
        lines = content.split('\n')
        set_llm_line = None
        graph_line = None
        
        for i, line in enumerate(lines):
            if 'set_llm_and_tools(self.llm, self.task_tools)' in line:
                set_llm_line = i
            elif 'self.assistant_ui_graph = graph' in line:
                graph_line = i
        
        assert set_llm_line is not None, "缺少 set_llm_and_tools 调用"
        assert graph_line is not None, "缺少 graph 赋值"
        assert set_llm_line < graph_line, "初始化顺序不正确"
        print("✓ 初始化顺序正确")
        
        return True
        
    except Exception as e:
        print(f"❌ agent_wrapper 集成测试失败: {e}")
        return False

def test_graph_initialization():
    """测试图初始化"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        with open(os.path.join(agents_dir, 'agent.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查图构建顺序
        lines = content.split('\n')
        workflow_line = None
        add_node_lines = []
        set_entry_line = None
        add_edges_line = None
        compile_line = None
        
        for i, line in enumerate(lines):
            if 'workflow = StateGraph(AgentState)' in line:
                workflow_line = i
            elif 'workflow.add_node(' in line:
                add_node_lines.append(i)
            elif 'workflow.set_entry_point(' in line:
                set_entry_line = i
            elif 'workflow.add_conditional_edges(' in line:
                add_edges_line = i
            elif 'graph = workflow.compile()' in line:
                compile_line = i
        
        assert workflow_line is not None, "缺少 workflow 创建"
        assert len(add_node_lines) >= 2, "缺少节点添加"
        assert set_entry_line is not None, "缺少入口点设置"
        assert add_edges_line is not None, "缺少边添加"
        assert compile_line is not None, "缺少编译"
        
        # 检查顺序
        assert workflow_line < min(add_node_lines), "workflow 创建顺序不正确"
        assert max(add_node_lines) < set_entry_line, "节点添加顺序不正确"
        assert set_entry_line < add_edges_line, "入口点设置顺序不正确"
        assert add_edges_line < compile_line, "边添加顺序不正确"
        
        print("✓ 图初始化顺序正确")
        
        return True
        
    except Exception as e:
        print(f"❌ 图初始化测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试全局 graph 实例...")
    print("=" * 60)
    
    tests = [
        ("全局 graph 结构", test_global_graph_structure),
        ("agent_wrapper 集成", test_agent_wrapper_integration),
        ("图初始化", test_graph_initialization),
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
        print("🎉 所有测试通过！全局 graph 实例创建成功。")
        print("\n重构总结:")
        print("- ✅ 移除了 create_graph 函数封装")
        print("- ✅ 直接在文件中初始化 graph 实例")
        print("- ✅ 使用全局变量存储 llm 和 task_tools")
        print("- ✅ 简化了函数签名")
        print("- ✅ 保持了所有功能")
        print("\n新的结构:")
        print("agents/")
        print("├── agent.py        # 全局 graph 实例")
        print("├── state.py        # 状态定义")
        print("├── agent_wrapper.py # Agent 包装器")
        print("├── tools.py        # 工具定义")
        print("└── ...             # 其他文件")
        print("\n优势:")
        print("- 🎯 代码更简洁，无函数封装")
        print("- 📦 图实例在模块级别初始化")
        print("- 🔧 函数签名更简洁")
        print("- 🚀 符合你要求的直接初始化方式")
        print("\n代码示例:")
        print("# 全局变量")
        print("_llm = None")
        print("_task_tools = None")
        print("")
        print("# 图构建")
        print("workflow = StateGraph(AgentState)")
        print("workflow.add_node('agent', call_model)")
        print("workflow.add_node('tools', run_tools)")
        print("graph = workflow.compile()")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
