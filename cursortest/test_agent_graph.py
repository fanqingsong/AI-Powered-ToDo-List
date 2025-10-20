"""
Agent Graph Builder 测试脚本

测试 agent.py 模块的功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from src.agents.agent_graph import AgentGraphBuilder, create_agent_graph_builder
from src.agents.tools import TaskTools
from src.agents.llm_config import get_llm
from src.services import TaskService


def test_agent_graph_builder():
    """测试 AgentGraphBuilder 的基本功能"""
    print("开始测试 AgentGraphBuilder...")
    
    try:
        # 初始化依赖
        llm = get_llm()
        task_service = TaskService()
        task_tools = TaskTools(task_service)
        
        # 创建图构建器
        graph_builder = create_agent_graph_builder(llm, task_tools)
        print("✓ 图构建器创建成功")
        
        # 测试构建 Assistant-UI 图
        assistant_ui_graph = graph_builder.build_assistant_ui_graph()
        print("✓ Assistant-UI 图构建成功")
        
        # 测试构建标准图
        standard_graph = graph_builder.build_standard_graph()
        print("✓ 标准图构建成功")
        
        # 测试构建自定义图
        def custom_node(state, config):
            return {"messages": "custom node executed"}
        
        custom_graph = graph_builder.build_custom_graph(
            custom_nodes={"custom": custom_node},
            custom_edges=[("agent", "custom"), ("custom", END)]
        )
        print("✓ 自定义图构建成功")
        
        print("\n所有测试通过！AgentGraphBuilder 工作正常。")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_agent_graph_builder()
