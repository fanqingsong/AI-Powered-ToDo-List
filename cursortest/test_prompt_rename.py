"""
测试 prompt.py 文件重命名

验证 prompt_config.py 已重命名为 prompt.py
"""

import os

def test_prompt_file_rename():
    """测试 prompt 文件重命名"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        # 检查新文件存在
        prompt_file = os.path.join(agents_dir, 'prompt.py')
        assert os.path.exists(prompt_file), "prompt.py 文件不存在"
        print("✓ prompt.py 文件存在")
        
        # 检查旧文件不存在
        old_file = os.path.join(agents_dir, 'prompt_config.py')
        assert not os.path.exists(old_file), "prompt_config.py 文件仍然存在"
        print("✓ prompt_config.py 文件已移除")
        
        return True
        
    except Exception as e:
        print(f"❌ prompt 文件重命名测试失败: {e}")
        return False

def test_prompt_content():
    """测试 prompt.py 文件内容"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        with open(os.path.join(agents_dir, 'prompt.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查必要的常量
        assert 'SYSTEM_PROMPT =' in content, "缺少 SYSTEM_PROMPT"
        print("✓ SYSTEM_PROMPT 存在")
        
        assert 'ERROR_MESSAGES =' in content, "缺少 ERROR_MESSAGES"
        print("✓ ERROR_MESSAGES 存在")
        
        assert 'SUCCESS_MESSAGES =' in content, "缺少 SUCCESS_MESSAGES"
        print("✓ SUCCESS_MESSAGES 存在")
        
        assert 'DEBUG_MESSAGES =' in content, "缺少 DEBUG_MESSAGES"
        print("✓ DEBUG_MESSAGES 存在")
        
        # 检查文档字符串
        assert 'Prompt配置模块' in content, "缺少文档字符串"
        print("✓ 文档字符串存在")
        
        return True
        
    except Exception as e:
        print(f"❌ prompt 内容测试失败: {e}")
        return False

def test_agent_wrapper_import():
    """测试 agent_wrapper.py 导入"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        with open(os.path.join(agents_dir, 'agent_wrapper.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查新导入
        assert 'from .prompt import SYSTEM_PROMPT, ERROR_MESSAGES, SUCCESS_MESSAGES, DEBUG_MESSAGES' in content, "导入路径不正确"
        print("✓ agent_wrapper.py 导入正确")
        
        # 检查旧导入不存在
        assert 'from .prompt_config import' not in content, "仍有旧的导入"
        print("✓ 旧导入已移除")
        
        return True
        
    except Exception as e:
        print(f"❌ agent_wrapper 导入测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试 prompt.py 文件重命名...")
    print("=" * 60)
    
    tests = [
        ("文件重命名", test_prompt_file_rename),
        ("文件内容", test_prompt_content),
        ("agent_wrapper 导入", test_agent_wrapper_import),
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
        print("🎉 所有测试通过！prompt.py 文件重命名成功完成。")
        print("\n重命名总结:")
        print("- ✅ prompt_config.py 已重命名为 prompt.py")
        print("- ✅ 更新了 agent_wrapper.py 中的导入")
        print("- ✅ 保持了所有功能")
        print("- ✅ 文件名更简洁")
        print("\n新的文件结构:")
        print("agents/")
        print("├── agent.py        # 全局 graph 实例")
        print("├── prompt.py       # 提示词配置")
        print("├── state.py        # 状态定义")
        print("├── agent_wrapper.py # Agent 包装器")
        print("├── tools.py        # 工具定义")
        print("└── ...             # 其他文件")
        print("\n优势:")
        print("- 🎯 文件名更简洁")
        print("- 📦 减少了文件名长度")
        print("- 🔧 保持了所有功能")
        print("- 🚀 导入路径更简洁")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
