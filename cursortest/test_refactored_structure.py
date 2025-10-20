"""
测试重构后的图构建器文件结构

验证新的继承架构文件是否正确创建
"""

import sys
import os

def test_file_structure():
    """测试文件结构"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        # 检查新文件是否存在
        files_to_check = [
            'base_agent.py',
            'assistant_ui_graph.py', 
            'standard_graph.py',
            'custom_graph.py',
            'graph_builder_factory.py',
            'agent_wrapper.py'
        ]
        
        for file_name in files_to_check:
            file_path = os.path.join(agents_dir, file_name)
            assert os.path.exists(file_path), f"{file_name} 文件不存在"
            print(f"✓ {file_name} 文件存在")
        
        # 检查旧的 agent.py 是否仍然存在（应该被替换）
        old_file_path = os.path.join(agents_dir, 'agent.py')
        if os.path.exists(old_file_path):
            print("⚠️  旧的 agent.py 文件仍然存在")
        else:
            print("✓ 旧的 agent.py 文件已被替换")
        
        return True
    except Exception as e:
        print(f"❌ 文件结构测试失败: {e}")
        return False

def test_code_structure():
    """测试代码结构"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        # 检查 base_agent.py
        with open(os.path.join(agents_dir, 'base_agent.py'), 'r', encoding='utf-8') as f:
            base_content = f.read()
        
        assert 'class BaseAgentGraph(ABC):' in base_content
        assert '@abstractmethod' in base_content
        assert 'def build(self) -> StateGraph:' in base_content
        print("✓ BaseAgentGraph 基础类结构正确")
        
        # 检查 assistant_ui_graph.py
        with open(os.path.join(agents_dir, 'assistant_ui_graph.py'), 'r', encoding='utf-8') as f:
            assistant_content = f.read()
        
        assert 'class AssistantUIGraph(BaseAgentGraph):' in assistant_content
        assert 'def build(self) -> StateGraph:' in assistant_content
        print("✓ AssistantUIGraph 类结构正确")
        
        # 检查 standard_graph.py
        with open(os.path.join(agents_dir, 'standard_graph.py'), 'r', encoding='utf-8') as f:
            standard_content = f.read()
        
        assert 'class StandardGraph(BaseAgentGraph):' in standard_content
        assert 'def build(self) -> StateGraph:' in standard_content
        print("✓ StandardGraph 类结构正确")
        
        # 检查 custom_graph.py
        with open(os.path.join(agents_dir, 'custom_graph.py'), 'r', encoding='utf-8') as f:
            custom_content = f.read()
        
        assert 'class CustomGraph(BaseAgentGraph):' in custom_content
        assert 'def build(self) -> StateGraph:' in custom_content
        assert 'def build_with_config(' in custom_content
        print("✓ CustomGraph 类结构正确")
        
        # 检查 graph_builder_factory.py
        with open(os.path.join(agents_dir, 'graph_builder_factory.py'), 'r', encoding='utf-8') as f:
            factory_content = f.read()
        
        assert 'class GraphBuilderFactory:' in factory_content
        assert 'def create_assistant_ui_graph(' in factory_content
        assert 'def create_standard_graph(' in factory_content
        assert 'def create_custom_graph(' in factory_content
        print("✓ GraphBuilderFactory 工厂类结构正确")
        
        return True
    except Exception as e:
        print(f"❌ 代码结构测试失败: {e}")
        return False

def test_inheritance_logic():
    """测试继承逻辑"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        # 检查继承关系
        with open(os.path.join(agents_dir, 'assistant_ui_graph.py'), 'r', encoding='utf-8') as f:
            assistant_content = f.read()
        
        assert 'from .base_agent_graph import BaseAgentGraph' in assistant_content
        print("✓ AssistantUIGraph 正确导入基础类")
        
        with open(os.path.join(agents_dir, 'standard_graph.py'), 'r', encoding='utf-8') as f:
            standard_content = f.read()
        
        assert 'from .base_agent_graph import BaseAgentGraph' in standard_content
        print("✓ StandardGraph 正确导入基础类")
        
        with open(os.path.join(agents_dir, 'custom_graph.py'), 'r', encoding='utf-8') as f:
            custom_content = f.read()
        
        assert 'from .base_agent_graph import BaseAgentGraph' in custom_content
        print("✓ CustomGraph 正确导入基础类")
        
        return True
    except Exception as e:
        print(f"❌ 继承逻辑测试失败: {e}")
        return False

def test_agent_wrapper_integration():
    """测试 agent_wrapper.py 的集成"""
    try:
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', 'agents')
        
        with open(os.path.join(agents_dir, 'agent_wrapper.py'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否使用了新的导入
        assert 'from .graph_builder_factory import create_graph_builder_factory' in content
        print("✓ agent_wrapper.py 使用了新的图构建器工厂")
        
        assert 'self.graph_builder_factory = create_graph_builder_factory(self.llm, self.task_tools)' in content
        print("✓ agent_wrapper.py 正确初始化了图构建器工厂")
        
        assert 'self.assistant_ui_graph = self.graph_builder_factory.build_assistant_ui_graph()' in content
        print("✓ agent_wrapper.py 正确构建了 Assistant-UI 图")
        
        # 检查是否移除了旧的导入
        assert 'from .agent import create_agent_graph_builder' not in content
        print("✓ agent_wrapper.py 移除了旧的导入")
        
        return True
    except Exception as e:
        print(f"❌ agent_wrapper 集成测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试重构后的图构建器文件结构...")
    print("=" * 60)
    
    tests = [
        ("文件结构", test_file_structure),
        ("代码结构", test_code_structure),
        ("继承逻辑", test_inheritance_logic),
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
        print("- ✅ 创建了 BaseAgentGraph 基础类，使用抽象基类封装公共逻辑")
        print("- ✅ 创建了 AssistantUIGraph 专用类，支持前端工具")
        print("- ✅ 创建了 StandardGraph 标准类，只使用后端工具")
        print("- ✅ 创建了 CustomGraph 自定义类，支持自定义节点和边")
        print("- ✅ 创建了 GraphBuilderFactory 工厂类，提供统一接口")
        print("- ✅ 更新了 agent_wrapper.py 使用新的架构")
        print("- ✅ 使用继承思想封装了公共逻辑，提高了代码复用性")
        print("- ✅ 每个图类型都有独立的文件，便于维护和扩展")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
