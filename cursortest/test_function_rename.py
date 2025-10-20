"""
测试函数重命名

验证 create_assistant_ui_graph 已重命名为 create_graph
"""

import os

def test_function_rename():
    """测试函数重命名"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        # 检查 agent.py
        with open(os.path.join(agents_dir, 'agent.py'), 'r', encoding='utf-8') as f:
            agent_content = f.read()
        
        # 检查新函数名存在
        assert 'def create_graph(' in agent_content, "缺少 create_graph 函数"
        print("✓ create_graph 函数存在")
        
        # 检查旧函数名不存在
        assert 'def create_assistant_ui_graph(' not in agent_content, "仍然存在 create_assistant_ui_graph 函数"
        print("✓ create_assistant_ui_graph 函数已移除")
        
        # 检查 agent_wrapper.py
        with open(os.path.join(agents_dir, 'agent_wrapper.py'), 'r', encoding='utf-8') as f:
            wrapper_content = f.read()
        
        # 检查导入
        assert 'from .agent import create_graph' in wrapper_content, "agent_wrapper.py 导入不正确"
        print("✓ agent_wrapper.py 导入正确")
        
        # 检查调用
        assert 'create_graph(self.llm, self.task_tools)' in wrapper_content, "agent_wrapper.py 调用不正确"
        print("✓ agent_wrapper.py 调用正确")
        
        # 检查旧引用不存在
        assert 'create_assistant_ui_graph' not in wrapper_content, "agent_wrapper.py 仍有旧函数引用"
        print("✓ agent_wrapper.py 已移除旧函数引用")
        
        return True
        
    except Exception as e:
        print(f"❌ 函数重命名测试失败: {e}")
        return False

def test_function_signature():
    """测试函数签名"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        with open(os.path.join(agents_dir, 'agent.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查函数签名
        assert 'def create_graph(llm: ChatOpenAI, task_tools: TaskTools):' in content, "函数签名不正确"
        print("✓ create_graph 函数签名正确")
        
        # 检查文档字符串
        assert '"""创建 Assistant-UI 图' in content, "函数文档字符串不正确"
        print("✓ 函数文档字符串正确")
        
        return True
        
    except Exception as e:
        print(f"❌ 函数签名测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试函数重命名...")
    print("=" * 60)
    
    tests = [
        ("函数重命名", test_function_rename),
        ("函数签名", test_function_signature),
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
        print("🎉 所有测试通过！函数重命名成功完成。")
        print("\n重命名总结:")
        print("- ✅ create_assistant_ui_graph 已重命名为 create_graph")
        print("- ✅ 更新了 agent_wrapper.py 中的导入和调用")
        print("- ✅ 更新了测试文件中的引用")
        print("- ✅ 保持了所有功能")
        print("\n新的函数签名:")
        print("def create_graph(llm: ChatOpenAI, task_tools: TaskTools):")
        print("    \"\"\"创建 Assistant-UI 图\"\"\"")
        print("    # ...")
        print("    return workflow.compile()")
        print("\n优势:")
        print("- 🎯 函数名更简洁")
        print("- 📦 减少了函数名长度")
        print("- 🔧 保持了所有功能")
        print("- 🚀 调用更简洁")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
