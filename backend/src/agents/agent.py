import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, AsyncGenerator
from ..services import TaskService
from ..services.conversation_service import ConversationService
from ..services.auth_service import AuthService
from ..models import ChatMessage
from .supervisor import graph as supervisor_graph, SupervisorState, get_supervisor_prompt
from langchain_core.messages import HumanMessage, AIMessage
from .llmconf import get_llm, is_llm_available
from .prompt import ERROR_MESSAGES, SUCCESS_MESSAGES, DEBUG_MESSAGES


class ResourceManagementAgent:
    """基于 Multi-Agent Supervisor 架构的资源管理 Agent
    
    使用Supervisor模式，支持plan-execute流程：
    - Supervisor负责规划和路由
    - Task/Schedule/Note子Agent负责具体执行
    """
    
    def __init__(self, task_service: TaskService):
        # task_service 参数保留以保持向后兼容，但不再存储为实例属性
        self.conversation_service = ConversationService()
        self.auth_service = AuthService()
        # Supervisor Graph已经在模块级别初始化，checkpointer和store已作为graph的属性
        # 用于Assistant-UI兼容的graph引用
        self.assistant_ui_graph = supervisor_graph
    
    def _is_llm_available(self) -> bool:
        """检查 LLM 是否可用"""
        return is_llm_available()
    
    async def process_message_stream(
        self, 
        message: str, 
        conversation_history: List[ChatMessage] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        frontend_tools_config: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式处理用户消息
        
        Args:
            message: 当前用户消息
            conversation_history: 对话历史，用于提供上下文（已废弃，现在从数据库加载）
            session_id: 会话ID，用于checkpointer和store
            user_id: 用户ID，用于会话关联
            frontend_tools_config: 前端工具配置
            
        Yields:
            Dict[str, Any]: 流式响应数据块
        """
        import asyncio
        
        print(f"[DEBUG] 开始流式处理消息，message: {message}, session_id: {session_id}, user_id: {user_id}")

        try:
            # 生成会话ID（如果没有提供）
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # 检查是否有可用的 LLM
            if not self._is_llm_available():
                yield {
                    'type': 'error',
                    'content': ERROR_MESSAGES["llm_unavailable"]
                }
                return
            
            # 从数据库加载会话历史
            db_conversation_history = await self.conversation_service.get_conversation_history(
                session_id=session_id,
                limit=20,
                user_id=user_id
            )
            
            # 获取用户基本信息
            user_info = ""
            if user_id:
                try:
                    if user_id.isdigit():
                        user = await self.auth_service.get_user_by_id(int(user_id))
                        if user:
                            user_info = f"""
当前登录用户信息：
- 用户ID: {user.id}
- 用户名: {user.username}
- 显示名称: {user.display_name}
- 邮箱: {user.email}
- 注册时间: {user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else '未知'}
- 最后登录: {user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else '未知'}
- 账户状态: {'活跃' if user.is_active else '非活跃'}
"""
                    else:
                        user_info = f"""
当前用户状态：未登录用户（会话ID: {user_id}）
"""
                except Exception as e:
                    print(f"获取用户信息失败: {e}")
            
            # 获取Supervisor系统提示词
            supervisor_prompt = get_supervisor_prompt()
            
            # 如果有用户信息，添加到系统提示词中
            if user_info:
                supervisor_prompt += f"\n\n{user_info}\n\n基于这些用户信息，你可以提供个性化的服务和建议。"
            
            # 获取用户ID（user_id现在通过SupervisorState传递）
            current_user_id = None
            if user_id and user_id.isdigit():
                current_user_id = int(user_id)
            
            # 构建SupervisorState初始状态
            initial_state: SupervisorState = {
                "messages": [HumanMessage(content=message)],
                "plan": None,
                "current_step": 0,
                "execution_results": [],
                "selected_agent": None,
                "agent_context": {
                    "user_message": message,
                    "user_info": user_info
                },
                "should_continue": True,
                "is_planning": True,
                "is_executing": False,
                "is_aggregating": False,
                "user_id": current_user_id  # 包含user_id到初始状态
            }

            print(f"[DEBUG] 即将调用 Supervisor Graph 流式处理，message: {message}")

            # 发送开始处理信号
            yield {
                'type': 'assistant',
                'content': '',
                'isStreaming': True
            }

            # 执行Supervisor图，使用流式处理
            config = {
                "configurable": {
                    "thread_id": session_id,
                },
                "recursion_limit": 50  # Supervisor可能需要更多递归
            }

            # 使用 astream 进行流式处理
            accumulated_content = ""
            async for chunk in supervisor_graph.astream(initial_state, config=config):
                # 处理各个节点的输出
                for node_name, node_output in chunk.items():
                    if node_name == "aggregate":
                        # 汇总节点输出最终响应
                        if "messages" in node_output:
                            messages = node_output["messages"]
                            if messages:
                                last_message = messages[-1]
                                if hasattr(last_message, 'content') and last_message.content:
                                    content = last_message.content
                                    if content != accumulated_content:
                                        new_content = content[len(accumulated_content):]
                                        accumulated_content = content
                                        
                                        # 发送内容块
                                        yield {
                                            'type': 'assistant',
                                            'content': new_content,
                                            'isStreaming': True
                                        }
                                        
                                        # 添加小延迟以模拟流式效果
                                        await asyncio.sleep(0.05)
                    
                    elif node_name in ["task_agent", "schedule_agent", "note_agent"]:
                        # 子Agent执行中，可以发送进度信息
                        yield {
                            'type': 'tool',
                            'content': f'正在执行{node_name}...',
                            'isStreaming': True
                        }
                    
                    elif node_name == "supervisor_plan":
                        # 规划阶段
                        if "plan" in node_output:
                            plan = node_output["plan"]
                            if plan and plan.get("summary"):
                                yield {
                                    'type': 'tool',
                                    'content': f'规划完成：{plan["summary"]}',
                                    'isStreaming': True
                                }
                    
                    elif node_name == "execute":
                        # 执行节点完成
                        if "execution_results" in node_output:
                            results = node_output["execution_results"]
                            if results:
                                last_result = results[-1]
                                if last_result.get("success"):
                                    yield {
                                        'type': 'tool',
                                        'content': f'步骤执行成功',
                                        'isStreaming': True
                                    }

            # 发送完成信号
            yield {
                'type': 'assistant',
                'content': '',
                'isStreaming': False
            }
            
            # 保存对话到会话历史数据库
            try:
                await self.conversation_service.save_conversation_turn(
                    session_id=session_id,
                    user_message=message,
                    assistant_response=accumulated_content,
                    user_id=user_id,
                    metadata={"agent": "langgraph_stream", "timestamp": datetime.utcnow().isoformat()}
                )
                print(SUCCESS_MESSAGES["conversation_saved"].format(session_id=session_id))
            except Exception as e:
                print(DEBUG_MESSAGES["conversation_save_failed"].format(error=e))
                import traceback
                traceback.print_exc()
            
        except Exception as e:
            print(f"Error in stream processing: {e}")
            import traceback
            traceback.print_exc()
            
            error_msg = str(e)
            if "404" in error_msg or "Connection error" in error_msg or "Resource not found" in error_msg:
                yield {
                    'type': 'error',
                    'content': ERROR_MESSAGES["connection_error"]
                }
            else:
                yield {
                    'type': 'error',
                    'content': ERROR_MESSAGES["general_error"].format(error_msg=error_msg)
                }
    
    async def cleanup(self):
        """清理资源"""
        pass

