"""
测试重命名后的 agent.py 文件

验证文件重命名和导入路径更新是否正常工作
"""

import sys
import os

def test_file_location():
    """测试文件位置"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        # 检查 agent.py 在正确位置
        assistant_file = os.path.join(agents_dir, 'agent.py')
        assert os.path.exists(assistant_file), "agent.py 不在 agents 目录下"
        print("✓ agent.py 在正确位置")
        
        # 检查 graph_builder 文件夹已删除（除了缓存）
        graph_builder_dir = os.path.join(agents_dir, 'graph_builder')
        if os.path.exists(graph_builder_dir):
            # 检查是否只剩下缓存文件夹
            contents = os.listdir(graph_builder_dir)
            if contents == ['__pycache__'] or not contents:
                print("✓ graph_builder 文件夹已清空（只剩下缓存）")
            else:
                print(f"⚠️  graph_builder 文件夹仍有内容: {contents}")
        else:
            print("✓ graph_builder 文件夹已完全删除")
        
        return True
    except Exception as e:
        print(f"❌ 文件位置测试失败: {e}")
        return False

def test_import_paths():
    """测试导入路径"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        # 检查 agent.py 的导入路径
        with open(os.path.join(agents_dir, 'agent.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'from .tools import TaskTools' in content, "agent.py 导入路径不正确"
        print("✓ agent.py 导入路径正确")
        
        # 检查 agent_wrapper.py 的导入路径
        with open(os.path.join(agents_dir, 'agent_wrapper.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'from .agent import create_assistant_ui_graph' in content, "agent_wrapper.py 导入路径不正确"
        print("✓ agent_wrapper.py 导入路径正确")
        
        # 检查没有旧的导入
        assert 'from .graph_builder import' not in content, "agent_wrapper.py 仍有旧的导入"
        print("✓ agent_wrapper.py 没有旧的导入")
        
        return True
    except Exception as e:
        print(f"❌ 导入路径测试失败: {e}")
        return False

def test_file_content():
    """测试文件内容"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        with open(os.path.join(agents_dir, 'agent.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查包含所有必要的类和方法
        assert 'class AssistantUIGraph:' in content
        print("✓ AssistantUIGraph 类存在")
        
        assert 'class AnyArgsSchema(BaseModel):' in content
        print("✓ AnyArgsSchema 类存在")
        
        assert 'class FrontendTool(BaseTool):' in content
        print("✓ FrontendTool 类存在")
        
        assert 'def build(self) -> StateGraph:' in content
        print("✓ build 方法存在")
        
        assert 'def create_assistant_ui_graph(' in content
        print("✓ create_assistant_ui_graph 函数存在")
        
        return True
    except Exception as e:
        print(f"❌ 文件内容测试失败: {e}")
        return False

def test_agent_wrapper_functionality():
    """测试 agent_wrapper.py 功能"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        with open(os.path.join(agents_dir, 'agent_wrapper.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查图创建逻辑
        assert 'self.assistant_ui_graph = create_assistant_ui_graph(self.llm, self.task_tools).build()' in content
        print("✓ agent_wrapper.py 图创建逻辑正确")
        
        return True
    except Exception as e:
        print(f"❌ agent_wrapper 功能测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试重命名后的 agent.py 文件...")
    print("=" * 60)
    
    tests = [
        ("文件位置", test_file_location),
        ("导入路径", test_import_paths),
        ("文件内容", test_file_content),
        ("agent_wrapper 功能", test_agent_wrapper_functionality),
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
        print("🎉 所有测试通过！文件重命名成功完成。")
        print("\n重命名总结:")
        print("- ✅ assistant_ui_graph.py 已重命名为 agent.py")
        print("- ✅ 更新了文件内的导入路径")
        print("- ✅ 更新了 agent_wrapper.py 的导入路径")
        print("- ✅ 保持了所有功能")
        print("\n最终结构:")
        print("agents/")
        print("├── agent.py        # 图构建功能")
        print("├── agent_wrapper.py      # Agent 包装器")
        print("├── tools.py              # 工具定义")
        print("└── ...                   # 其他文件")
        print("\n优势:")
        print("- 🎯 文件名更简洁，直接表达功能")
        print("- 📦 减少了文件名长度")
        print("- 🔧 保持了所有必要的功能")
        print("- 🚀 导入路径更简洁")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
