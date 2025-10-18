import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, delete, func, and_, desc
from sqlalchemy.orm import selectinload
from ..database import get_db_session
from ..models import (
    ConversationMessage, ConversationHistory, ConversationRequest, ConversationResponse
)
from ..models.database_models import ConversationHistoryDB


class ConversationService:
    """会话历史服务"""
    
    def __init__(self):
        self.max_messages_per_session = 100  # 每个会话最多保存的消息数量
        self.conversation_retention_days = 30  # 会话保留天数
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationMessage:
        """添加消息到会话历史"""
        async with get_db_session() as session:
            # 获取当前会话的下一个消息顺序
            next_order_query = select(func.max(ConversationHistoryDB.message_order)).where(
                ConversationHistoryDB.session_id == session_id
            )
            result = await session.execute(next_order_query)
            next_order = result.scalar() or 0
            next_order += 1
            
            # 创建数据库记录
            db_message = ConversationHistoryDB(
                session_id=session_id,
                user_id=user_id,
                role=role,
                content=content,
                message_order=next_order,
                message_metadata=metadata
            )
            
            session.add(db_message)
            await session.flush()  # 获取ID
            
            # 转换为Pydantic模型
            message = ConversationMessage(
                id=db_message.id,
                session_id=db_message.session_id,
                user_id=db_message.user_id,
                role=db_message.role,
                content=db_message.content,
                message_order=db_message.message_order,
                metadata=db_message.message_metadata,
                created_at=db_message.created_at
            )
            
            return message
    
    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 50,
        user_id: Optional[str] = None
    ) -> List[ConversationMessage]:
        """获取会话历史"""
        async with get_db_session() as session:
            query = select(ConversationHistoryDB).where(
                ConversationHistoryDB.session_id == session_id
            ).order_by(ConversationHistoryDB.message_order.asc()).limit(limit)
            
            if user_id:
                query = query.where(ConversationHistoryDB.user_id == user_id)
            
            result = await session.execute(query)
            db_messages = result.scalars().all()
            
            messages = []
            for db_message in db_messages:
                message = ConversationMessage(
                    id=db_message.id,
                    session_id=db_message.session_id,
                    user_id=db_message.user_id,
                    role=db_message.role,
                    content=db_message.content,
                    message_order=db_message.message_order,
                    metadata=db_message.message_metadata,
                    created_at=db_message.created_at
                )
                messages.append(message)
            
            return messages
    
    async def clear_conversation_history(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """清空会话历史"""
        async with get_db_session() as session:
            query = delete(ConversationHistoryDB).where(
                ConversationHistoryDB.session_id == session_id
            )
            
            if user_id:
                query = query.where(ConversationHistoryDB.user_id == user_id)
            
            await session.execute(query)
            return True
    
    async def get_conversation_stats(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取会话统计信息"""
        async with get_db_session() as session:
            # 获取消息总数
            count_query = select(func.count(ConversationHistoryDB.id)).where(
                ConversationHistoryDB.session_id == session_id
            )
            
            if user_id:
                count_query = count_query.where(ConversationHistoryDB.user_id == user_id)
            
            result = await session.execute(count_query)
            total_messages = result.scalar() or 0
            
            # 获取最后一条消息时间
            last_message_query = select(ConversationHistoryDB.created_at).where(
                ConversationHistoryDB.session_id == session_id
            ).order_by(desc(ConversationHistoryDB.created_at)).limit(1)
            
            if user_id:
                last_message_query = last_message_query.where(ConversationHistoryDB.user_id == user_id)
            
            result = await session.execute(last_message_query)
            last_message_time = result.scalar()
            
            return {
                "session_id": session_id,
                "total_messages": total_messages,
                "last_message_time": last_message_time.isoformat() if last_message_time else None,
                "user_id": user_id
            }
    
    async def cleanup_old_conversations(self) -> int:
        """清理过期会话"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.conversation_retention_days)
        
        async with get_db_session() as session:
            query = delete(ConversationHistoryDB).where(
                ConversationHistoryDB.created_at < cutoff_date
            )
            result = await session.execute(query)
            return result.rowcount
    
    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取用户的所有会话"""
        async with get_db_session() as session:
            # 获取每个会话的最新消息时间
            query = select(
                ConversationHistoryDB.session_id,
                func.max(ConversationHistoryDB.created_at).label('last_activity'),
                func.count(ConversationHistoryDB.id).label('message_count')
            ).where(
                ConversationHistoryDB.user_id == user_id
            ).group_by(
                ConversationHistoryDB.session_id
            ).order_by(
                desc('last_activity')
            ).limit(limit)
            
            result = await session.execute(query)
            sessions = []
            
            for row in result:
                sessions.append({
                    "session_id": row.session_id,
                    "last_activity": row.last_activity.isoformat() if row.last_activity else None,
                    "message_count": row.message_count
                })
            
            return sessions
    
    async def save_conversation_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """保存对话轮次（用户消息 + 助手回复）"""
        try:
            # 保存用户消息
            await self.add_message(
                session_id=session_id,
                role="user",
                content=user_message,
                user_id=user_id,
                metadata=metadata
            )
            
            # 保存助手回复
            await self.add_message(
                session_id=session_id,
                role="assistant",
                content=assistant_response,
                user_id=user_id,
                metadata=metadata
            )
            
            return True
        except Exception as e:
            print(f"保存对话轮次失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def get_conversation_context_for_agent(
        self,
        session_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取用于Agent的对话上下文"""
        try:
            messages = await self.get_conversation_history(session_id, limit)
            
            context = []
            for message in messages:
                context.append({
                    "role": message.role,
                    "content": message.content,
                    "timestamp": message.created_at.isoformat() if message.created_at else None,
                    "metadata": message.metadata or {}
                })
            
            return context
        except Exception as e:
            print(f"获取对话上下文失败: {e}")
            return []
