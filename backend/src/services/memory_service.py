import asyncio
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from sqlalchemy import select, update, delete, func, and_, or_, text
from sqlalchemy.orm import selectinload
from ..database import get_db_session
from ..models import (
    ShortTermMemory, LongTermMemory, TaskContextMemory,
    MemoryType, MessageType, ContextType, MemorySearchRequest, MemorySearchResult
)
from ..models.database_models import ShortTermMemoryDB, LongTermMemoryDB, TaskContextMemoryDB


class MemoryService:
    """记忆存储服务"""
    
    def __init__(self):
        self.max_short_term_memories = 100  # 每个会话最多保存的短期记忆数量
        self.memory_retention_days = 30     # 短期记忆保留天数
    
    # 短期记忆管理
    async def add_short_term_memory(
        self, 
        session_id: str, 
        message_type: MessageType, 
        content: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ShortTermMemory:
        """添加短期记忆"""
        async with get_db_session() as session:
            # 创建数据库记录
            db_memory = ShortTermMemoryDB(
                session_id=session_id,
                user_id=user_id,
                message_type=message_type.value,
                content=content,
                message_metadata=metadata
            )
            
            session.add(db_memory)
            await session.flush()  # 获取ID
            
            # 转换为Pydantic模型
            memory = ShortTermMemory(
                id=db_memory.id,
                session_id=db_memory.session_id,
                user_id=db_memory.user_id,
                message_type=MessageType(db_memory.message_type),
                content=db_memory.content,
                metadata=db_memory.message_metadata,
                created_at=db_memory.created_at,
                updated_at=db_memory.updated_at
            )
            
            return memory
    
    async def get_short_term_memories(
        self, 
        session_id: str, 
        limit: int = 50,
        user_id: Optional[str] = None
    ) -> List[ShortTermMemory]:
        """获取短期记忆"""
        async with get_db_session() as session:
            query = select(ShortTermMemoryDB).where(
                ShortTermMemoryDB.session_id == session_id
            ).order_by(ShortTermMemoryDB.created_at.desc()).limit(limit)
            
            if user_id:
                query = query.where(ShortTermMemoryDB.user_id == user_id)
            
            result = await session.execute(query)
            db_memories = result.scalars().all()
            
            memories = []
            for db_memory in db_memories:
                memory = ShortTermMemory(
                    id=db_memory.id,
                    session_id=db_memory.session_id,
                    user_id=db_memory.user_id,
                    message_type=MessageType(db_memory.message_type),
                    content=db_memory.content,
                    metadata=db_memory.message_metadata,
                    created_at=db_memory.created_at,
                    updated_at=db_memory.updated_at
                )
                memories.append(memory)
            
            return memories
    
    async def clear_short_term_memories(self, session_id: str) -> bool:
        """清空指定会话的短期记忆"""
        async with get_db_session() as session:
            query = delete(ShortTermMemoryDB).where(
                ShortTermMemoryDB.session_id == session_id
            )
            await session.execute(query)
            return True
    
    # 长期记忆管理
    async def add_long_term_memory(
        self,
        memory_type: MemoryType,
        key: str,
        value: str,
        user_id: Optional[str] = None,
        importance_score: int = 1
    ) -> LongTermMemory:
        """添加长期记忆"""
        async with get_db_session() as session:
            # 检查是否已存在相同的key
            existing_query = select(LongTermMemoryDB).where(
                and_(
                    LongTermMemoryDB.key == key,
                    LongTermMemoryDB.user_id == user_id
                )
            )
            existing_result = await session.execute(existing_query)
            existing_memory = existing_result.scalar_one_or_none()
            
            if existing_memory:
                # 更新现有记忆
                existing_memory.value = value
                existing_memory.importance_score = importance_score
                existing_memory.updated_at = datetime.utcnow()
                db_memory = existing_memory
            else:
                # 创建新记忆
                db_memory = LongTermMemoryDB(
                    user_id=user_id,
                    memory_type=memory_type.value,
                    key=key,
                    value=value,
                    importance_score=importance_score
                )
                session.add(db_memory)
            
            await session.flush()
            
            # 转换为Pydantic模型
            memory = LongTermMemory(
                id=db_memory.id,
                user_id=db_memory.user_id,
                memory_type=MemoryType(db_memory.memory_type),
                key=db_memory.key,
                value=db_memory.value,
                importance_score=db_memory.importance_score,
                access_count=db_memory.access_count,
                last_accessed=db_memory.last_accessed,
                created_at=db_memory.created_at,
                updated_at=db_memory.updated_at
            )
            
            return memory
    
    async def get_long_term_memories(
        self,
        user_id: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        query: Optional[str] = None,
        limit: int = 10
    ) -> List[LongTermMemory]:
        """获取长期记忆"""
        # 这里需要实际的数据库查询
        return []
    
    async def update_memory_access(self, memory_id: int) -> bool:
        """更新记忆访问次数和最后访问时间"""
        # 这里需要实际的数据库更新操作
        return True
    
    async def search_memories(
        self, 
        search_request: MemorySearchRequest
    ) -> MemorySearchResult:
        """搜索记忆"""
        # 这里需要实际的数据库搜索操作
        return MemorySearchResult(
            memories=[],
            total_count=0,
            search_query=search_request.query
        )
    
    # 任务上下文记忆管理
    async def add_task_context_memory(
        self,
        session_id: str,
        context_type: ContextType,
        context_data: Dict[str, Any],
        task_id: Optional[int] = None
    ) -> TaskContextMemory:
        """添加任务上下文记忆"""
        async with get_db_session() as session:
            memory = TaskContextMemory(
                session_id=session_id,
                task_id=task_id,
                context_type=context_type,
                context_data=context_data,
                created_at=datetime.utcnow()
            )
            
            # 这里需要实际的数据库操作
            return memory
    
    async def get_task_context_memories(
        self,
        session_id: str,
        task_id: Optional[int] = None,
        context_type: Optional[ContextType] = None
    ) -> List[TaskContextMemory]:
        """获取任务上下文记忆"""
        # 这里需要实际的数据库查询
        return []
    
    # 记忆清理和维护
    async def cleanup_old_memories(self) -> Dict[str, int]:
        """清理过期记忆"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.memory_retention_days)
        
        # 这里需要实际的数据库清理操作
        return {
            "short_term_cleaned": 0,
            "long_term_cleaned": 0,
            "task_context_cleaned": 0
        }
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        # 这里需要实际的数据库统计查询
        return {
            "total_short_term": 0,
            "total_long_term": 0,
            "total_task_context": 0,
            "active_sessions": 0
        }
    
    # LangGraph 集成方法
    async def get_conversation_context(
        self, 
        session_id: str, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取对话上下文，用于LangGraph"""
        try:
            memories = await self.get_short_term_memories(session_id, limit)
            
            context = []
            for memory in memories:
                context.append({
                    "role": memory.message_type.value,
                    "content": memory.content,
                    "timestamp": memory.created_at.isoformat() if memory.created_at else None,
                    "metadata": memory.metadata or {}
                })
            
            return context
        except Exception as e:
            print(f"获取对话上下文失败: {e}")
            return []
    
    async def save_conversation_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """保存对话轮次"""
        try:
            print(f"开始保存对话轮次: session_id={session_id}")
            
            # 保存用户消息
            print("保存用户消息...")
            await self.add_short_term_memory(
                session_id=session_id,
                message_type=MessageType.USER,
                content=user_message,
                user_id=user_id,
                metadata=metadata
            )
            print("用户消息保存成功")
            
            # 保存助手回复
            print("保存助手回复...")
            await self.add_short_term_memory(
                session_id=session_id,
                message_type=MessageType.ASSISTANT,
                content=assistant_response,
                user_id=user_id,
                metadata=metadata
            )
            print("助手回复保存成功")
            
            return True
        except Exception as e:
            print(f"保存对话轮次失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def extract_and_save_knowledge(
        self,
        session_id: str,
        content: str,
        user_id: Optional[str] = None
    ) -> bool:
        """从对话中提取并保存知识"""
        # 这里可以实现知识提取逻辑
        # 例如：提取任务相关信息、用户偏好等
        try:
            # 示例：如果内容包含任务信息，保存为长期记忆
            if "任务" in content and "ID" in content:
                await self.add_long_term_memory(
                    memory_type=MemoryType.CONTEXT,
                    key=f"task_context_{session_id}",
                    value=content,
                    user_id=user_id,
                    importance_score=5
                )
            
            return True
        except Exception as e:
            print(f"提取知识失败: {e}")
            return False
