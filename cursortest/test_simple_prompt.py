#!/usr/bin/env python3
"""
简单测试动态系统提示词生成功能
"""

def test_prompt_template():
    """测试基础模板功能"""
    print("=== 测试基础模板功能 ===")
    
    # 基础系统提示词模板
    BASE_SYSTEM_PROMPT_TEMPLATE = """你是一个智能的AI助手，专门帮助用户管理任务和提供个性化服务。

## 你的身份和能力：
- 你是用户的专属AI助手，能够识别和记住用户身份
- 你可以帮助用户管理任务、回答问题、提供建议
- 你具有记忆能力，能够记住用户的偏好和历史对话
- 你能够访问用户的登录信息，提供精准的个性化服务

## 可用的工具：
{tools_description}

## 重要指导原则：
- 当用户询问"我是谁"或身份相关问题时，你应该：
  * 直接使用提供的用户信息回答
  * 展现你对用户身份的准确了解
  * 提供个性化的回答，体现专属服务
- 当用户要求创建任务时，必须调用create_task_tool工具
- 当用户要求查看任务时，必须调用get_tasks_tool工具
- 当用户要求更新任务时，必须调用update_task_tool工具
- 当用户要求删除任务时，必须调用delete_task_tool、delete_task_by_title_tool或delete_latest_task_tool工具
- 当用户要求打开系统设置、任务管理、日程安排、笔记管理、数据分析等页面时，必须调用navigate_to_page_tool工具
- 不要说"无法执行"或"出现问题"，而是直接调用相应的工具
- 始终保持友好、专业的语调
- 展现你的智能和个性化服务能力
- 基于用户信息提供精准的服务和建议

请用中文回复用户，并展现你的智能和个性化服务能力。"""

    # 模拟工具定义
    mock_tool_definitions = [
        {
            "function": {
                "name": "create_task_tool",
                "description": "创建新任务"
            }
        },
        {
            "function": {
                "name": "get_tasks_tool", 
                "description": "获取所有任务列表"
            }
        },
        {
            "function": {
                "name": "delete_task_by_title_tool",
                "description": "根据任务名称删除任务"
            }
        }
    ]
    
    # 构建工具描述
    tool_descriptions = []
    for i, tool_def in enumerate(mock_tool_definitions, 1):
        tool_name = tool_def["function"]["name"]
        tool_desc = tool_def["function"]["description"]
        
        # 格式化工具描述
        if tool_name.startswith("_"):
            # 移除下划线前缀
            display_name = tool_name[1:]
        else:
            display_name = tool_name
            
        tool_descriptions.append(f"{i}. {display_name} - {tool_desc}")
    
    tools_description = "\n".join(tool_descriptions)
    
    # 生成动态系统提示词
    dynamic_prompt = BASE_SYSTEM_PROMPT_TEMPLATE.format(tools_description=tools_description)
    
    print("生成的动态系统提示词:")
    print(dynamic_prompt)
    print("\n" + "="*50 + "\n")

def test_frontend_tools():
    """测试前端工具集成"""
    print("=== 测试前端工具集成 ===")
    
    BASE_SYSTEM_PROMPT_TEMPLATE = """你是一个智能的AI助手，专门帮助用户管理任务和提供个性化服务。

## 可用的工具：
{tools_description}

请用中文回复用户，并展现你的智能和个性化服务能力。"""

    # 模拟后端工具
    backend_tools_desc = """1. create_task_tool - 创建新任务
2. get_tasks_tool - 获取所有任务列表
3. delete_task_by_title_tool - 根据任务名称删除任务"""
    
    # 模拟前端工具配置
    frontend_tools_config = [
        {
            "name": "custom_frontend_tool",
            "description": "自定义前端工具"
        },
        {
            "name": "another_frontend_tool", 
            "description": "另一个前端工具"
        }
    ]
    
    # 添加前端工具描述
    frontend_tools_desc = []
    start_index = 4  # 后端工具有3个，从4开始
    
    for i, tool_config in enumerate(frontend_tools_config, start_index):
        tool_name = tool_config.get("name", f"frontend_tool_{i}")
        tool_desc = tool_config.get("description", "前端工具")
        frontend_tools_desc.append(f"{i}. {tool_name} - {tool_desc}")
    
    tools_description = backend_tools_desc + "\n" + "\n".join(frontend_tools_desc)
    
    # 生成动态系统提示词
    dynamic_prompt = BASE_SYSTEM_PROMPT_TEMPLATE.format(tools_description=tools_description)
    
    print("生成的带前端工具的动态系统提示词:")
    print(dynamic_prompt)
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    print("开始测试动态系统提示词功能...\n")
    
    try:
        test_prompt_template()
        test_frontend_tools()
        
        print("✅ 所有测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
