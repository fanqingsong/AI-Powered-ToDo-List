"""
测试新创建的 state.py 文件

验证 AgentState 定义是否正确
"""

import os
import sys

def test_state_file_exists():
    """测试 state.py 文件是否存在"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        state_file = os.path.join(agents_dir, 'state.py')
        
        assert os.path.exists(state_file), "state.py 文件不存在"
        print("✓ state.py 文件存在")
        
        return True
    except Exception as e:
        print(f"❌ state.py 文件存在性测试失败: {e}")
        return False

def test_state_content():
    """测试 state.py 文件内容"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        with open(os.path.join(agents_dir, 'state.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查必要的导入
        assert 'from typing import Annotated' in content, "缺少 Annotated 导入"
        print("✓ Annotated 导入存在")
        
        assert 'from typing_extensions import TypedDict' in content, "缺少 TypedDict 导入"
        print("✓ TypedDict 导入存在")
        
        assert 'from langgraph.graph.message import add_messages' in content, "缺少 add_messages 导入"
        print("✓ add_messages 导入存在")
        
        # 检查 AgentState 类定义
        assert 'class AgentState(TypedDict):' in content, "缺少 AgentState 类定义"
        print("✓ AgentState 类定义存在")
        
        assert 'messages: Annotated[list, add_messages]' in content, "缺少 messages 字段定义"
        print("✓ messages 字段定义存在")
        
        return True
    except Exception as e:
        print(f"❌ state.py 内容测试失败: {e}")
        return False

def test_agent_integration():
    """测试 agent.py 是否正确引用了 state.py"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        with open(os.path.join(agents_dir, 'agent.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查导入
        assert 'from .state import AgentState' in content, "agent.py 缺少 AgentState 导入"
        print("✓ agent.py 正确导入 AgentState")
        
        # 检查使用
        assert 'StateGraph(AgentState)' in content, "agent.py 没有使用 AgentState"
        print("✓ agent.py 正确使用 AgentState")
        
        # 检查不再使用 MessagesState
        assert 'MessagesState' not in content, "agent.py 仍在使用 MessagesState"
        print("✓ agent.py 已移除 MessagesState 使用")
        
        return True
    except Exception as e:
        print(f"❌ agent.py 集成测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试新创建的 state.py 文件...")
    print("=" * 60)
    
    tests = [
        ("文件存在性", test_state_file_exists),
        ("文件内容", test_state_content),
        ("agent.py 集成", test_agent_integration),
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
        print("🎉 所有测试通过！state.py 文件创建成功。")
        print("\n创建总结:")
        print("- ✅ 创建了 state.py 文件")
        print("- ✅ 定义了 AgentState TypedDict")
        print("- ✅ 使用 Annotated[list, add_messages] 定义 messages 字段")
        print("- ✅ agent.py 正确引用新的状态定义")
        print("- ✅ 移除了对 MessagesState 的依赖")
        print("\n新的文件结构:")
        print("agents/")
        print("├── agent.py        # 图构建功能")
        print("├── state.py        # 状态定义")
        print("├── agent_wrapper.py # Agent 包装器")
        print("├── tools.py        # 工具定义")
        print("└── ...             # 其他文件")
        print("\n优势:")
        print("- 🎯 状态定义独立，便于维护")
        print("- 📦 符合 LangGraph 最佳实践")
        print("- 🔧 类型安全，IDE 支持更好")
        print("- 🚀 代码结构更清晰")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
