from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import re
import logging

from ..models.database_models import NoteDB, NoteCategory, UserDB
from ..models.note import (
    NoteCreate, NoteUpdate, NoteResponse, NoteListResponse, 
    NoteSearchRequest, NoteStatsResponse, NoteCategoryEnum
)
from ..integrations.celery_client import enqueue_sync_note, enqueue_delete_note

logger = logging.getLogger(__name__)


class NoteService:
    """笔记管理服务"""
    
    def __init__(self):
        pass
    
    async def create_note(self, db: AsyncSession, note_data: NoteCreate, user_id: int) -> NoteResponse:
        """创建笔记"""
        # 计算字数
        word_count = len(note_data.content)
        
        # 创建笔记对象
        db_note = NoteDB(
            title=note_data.title,
            content=note_data.content,
            category=note_data.category.value,
            user_id=user_id,
            tags=note_data.tags or [],
            is_pinned=note_data.is_pinned,
            is_archived=note_data.is_archived,
            word_count=word_count
        )
        
        db.add(db_note)
        await db.commit()
        await db.refresh(db_note)
        
        # 即时同步到向量数据库（通过 Celery 任务名异步派发）
        try:
            enqueue_sync_note(db_note.id, user_id)
            logger.info(f"已派发笔记 {db_note.id} 的向量数据库同步任务")
        except Exception as e:
            logger.error(f"派发笔记 {db_note.id} 向量数据库同步失败: {e}")
        
        return NoteResponse.model_validate(db_note)
    
    async def get_note(self, db: AsyncSession, note_id: int, user_id: int) -> Optional[NoteResponse]:
        """获取单个笔记"""
        result = await db.execute(
            select(NoteDB).where(
                and_(NoteDB.id == note_id, NoteDB.user_id == user_id)
            )
        )
        db_note = result.scalar_one_or_none()
        
        if db_note:
            # 更新最后访问时间
            db_note.last_accessed = datetime.utcnow()
            await db.commit()
            return NoteResponse.model_validate(db_note)
        
        return None
    
    async def update_note(self, db: AsyncSession, note_id: int, note_data: NoteUpdate, user_id: int) -> Optional[NoteResponse]:
        """更新笔记"""
        result = await db.execute(
            select(NoteDB).where(
                and_(NoteDB.id == note_id, NoteDB.user_id == user_id)
            )
        )
        db_note = result.scalar_one_or_none()
        
        if not db_note:
            return None
        
        # 更新字段
        update_data = note_data.dict(exclude_unset=True)
        
        # 如果更新了内容，重新计算字数
        if 'content' in update_data:
            update_data['word_count'] = len(update_data['content'])
        
        # 如果更新了分类，需要转换枚举值
        if 'category' in update_data:
            update_data['category'] = update_data['category'].value
        
        for field, value in update_data.items():
            setattr(db_note, field, value)
        
        await db.commit()
        await db.refresh(db_note)
        
        # 即时同步到向量数据库（通过 Celery 任务名异步派发）
        try:
            enqueue_sync_note(db_note.id, user_id)
            logger.info(f"已派发笔记 {db_note.id} 的向量数据库更新同步任务")
        except Exception as e:
            logger.error(f"派发笔记 {db_note.id} 向量数据库更新同步失败: {e}")
        
        return NoteResponse.model_validate(db_note)
    
    async def delete_note(self, db: AsyncSession, note_id: int, user_id: int) -> bool:
        """删除笔记"""
        result = await db.execute(
            select(NoteDB).where(
                and_(NoteDB.id == note_id, NoteDB.user_id == user_id)
            )
        )
        db_note = result.scalar_one_or_none()
        
        if not db_note:
            return False
        
        await db.delete(db_note)
        await db.commit()
        
        # 即时从向量数据库中删除（通过 Celery 任务名异步派发）
        try:
            enqueue_delete_note(note_id, user_id)
            logger.info(f"已派发笔记 {note_id} 的向量数据库删除任务")
        except Exception as e:
            logger.error(f"派发笔记 {note_id} 向量数据库删除失败: {e}")
        
        return True
    
    async def search_notes(self, db: AsyncSession, search_request: NoteSearchRequest, user_id: int) -> NoteListResponse:
        """搜索笔记"""
        # 构建查询条件
        conditions = [NoteDB.user_id == user_id]
        
        # 关键词搜索
        if search_request.query:
            search_term = f"%{search_request.query}%"
            conditions.append(
                or_(
                    NoteDB.title.ilike(search_term),
                    NoteDB.content.ilike(search_term)
                )
            )
        
        # 分类筛选
        if search_request.category:
            conditions.append(NoteDB.category == search_request.category.value)
        
        # 标签筛选
        if search_request.tags:
            for tag in search_request.tags:
                conditions.append(NoteDB.tags.contains([tag]))
        
        # 置顶筛选
        if search_request.is_pinned is not None:
            conditions.append(NoteDB.is_pinned == search_request.is_pinned)
        
        # 归档筛选
        if search_request.is_archived is not None:
            conditions.append(NoteDB.is_archived == search_request.is_archived)
        
        # 构建查询
        query = select(NoteDB).where(and_(*conditions))
        
        # 排序
        if search_request.sort_by == "created_at":
            order_by = NoteDB.created_at
        elif search_request.sort_by == "updated_at":
            order_by = NoteDB.updated_at
        elif search_request.sort_by == "title":
            order_by = NoteDB.title
        elif search_request.sort_by == "word_count":
            order_by = NoteDB.word_count
        else:
            order_by = NoteDB.updated_at
        
        if search_request.sort_order == "asc":
            query = query.order_by(asc(order_by))
        else:
            query = query.order_by(desc(order_by))
        
        # 分页
        offset = (search_request.page - 1) * search_request.page_size
        query = query.offset(offset).limit(search_request.page_size)
        
        # 执行查询
        result = await db.execute(query)
        notes = result.scalars().all()
        
        # 获取总数
        count_query = select(func.count(NoteDB.id)).where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # 计算总页数
        total_pages = (total + search_request.page_size - 1) // search_request.page_size
        
        return NoteListResponse(
            notes=[NoteResponse.from_orm(note) for note in notes],
            total=total,
            page=search_request.page,
            page_size=search_request.page_size,
            total_pages=total_pages
        )
    
    async def get_notes_by_category(self, db: AsyncSession, category: NoteCategoryEnum, user_id: int, limit: int = 20) -> List[NoteResponse]:
        """根据分类获取笔记"""
        result = await db.execute(
            select(NoteDB)
            .where(
                and_(
                    NoteDB.user_id == user_id,
                    NoteDB.category == category.value,
                    NoteDB.is_archived == False
                )
            )
            .order_by(desc(NoteDB.updated_at))
            .limit(limit)
        )
        notes = result.scalars().all()
        
        return [NoteResponse.model_validate(note) for note in notes]
    
    async def get_pinned_notes(self, db: AsyncSession, user_id: int) -> List[NoteResponse]:
        """获取置顶笔记"""
        result = await db.execute(
            select(NoteDB)
            .where(
                and_(
                    NoteDB.user_id == user_id,
                    NoteDB.is_pinned == True,
                    NoteDB.is_archived == False
                )
            )
            .order_by(desc(NoteDB.updated_at))
        )
        notes = result.scalars().all()
        
        return [NoteResponse.model_validate(note) for note in notes]
    
    async def get_recent_notes(self, db: AsyncSession, user_id: int, days: int = 7, limit: int = 20) -> List[NoteResponse]:
        """获取最近笔记"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        result = await db.execute(
            select(NoteDB)
            .where(
                and_(
                    NoteDB.user_id == user_id,
                    NoteDB.created_at >= since_date,
                    NoteDB.is_archived == False
                )
            )
            .order_by(desc(NoteDB.created_at))
            .limit(limit)
        )
        notes = result.scalars().all()
        
        return [NoteResponse.model_validate(note) for note in notes]
    
    async def get_note_stats(self, db: AsyncSession, user_id: int) -> NoteStatsResponse:
        """获取笔记统计信息"""
        # 总笔记数
        total_result = await db.execute(
            select(func.count(NoteDB.id)).where(NoteDB.user_id == user_id)
        )
        total_notes = total_result.scalar()
        
        # 按分类统计
        category_result = await db.execute(
            select(NoteDB.category, func.count(NoteDB.id))
            .where(NoteDB.user_id == user_id)
            .group_by(NoteDB.category)
        )
        notes_by_category = {row[0]: row[1] for row in category_result.fetchall()}
        
        # 总字数
        word_count_result = await db.execute(
            select(func.sum(NoteDB.word_count)).where(NoteDB.user_id == user_id)
        )
        total_words = word_count_result.scalar() or 0
        
        # 置顶笔记数
        pinned_result = await db.execute(
            select(func.count(NoteDB.id)).where(
                and_(
                    NoteDB.user_id == user_id,
                    NoteDB.is_pinned == True
                )
            )
        )
        pinned_notes = pinned_result.scalar()
        
        # 归档笔记数
        archived_result = await db.execute(
            select(func.count(NoteDB.id)).where(
                and_(
                    NoteDB.user_id == user_id,
                    NoteDB.is_archived == True
                )
            )
        )
        archived_notes = archived_result.scalar()
        
        # 最近7天创建的笔记数
        since_date = datetime.utcnow() - timedelta(days=7)
        recent_result = await db.execute(
            select(func.count(NoteDB.id)).where(
                and_(
                    NoteDB.user_id == user_id,
                    NoteDB.created_at >= since_date
                )
            )
        )
        recent_notes = recent_result.scalar()
        
        return NoteStatsResponse(
            total_notes=total_notes,
            notes_by_category=notes_by_category,
            total_words=total_words,
            pinned_notes=pinned_notes,
            archived_notes=archived_notes,
            recent_notes=recent_notes
        )
    
    async def toggle_pin(self, db: AsyncSession, note_id: int, user_id: int) -> Optional[NoteResponse]:
        """切换置顶状态"""
        result = await db.execute(
            select(NoteDB).where(
                and_(NoteDB.id == note_id, NoteDB.user_id == user_id)
            )
        )
        db_note = result.scalar_one_or_none()
        
        if not db_note:
            return None
        
        db_note.is_pinned = not db_note.is_pinned
        await db.commit()
        await db.refresh(db_note)
        
        return NoteResponse.model_validate(db_note)
    
    async def toggle_archive(self, db: AsyncSession, note_id: int, user_id: int) -> Optional[NoteResponse]:
        """切换归档状态"""
        result = await db.execute(
            select(NoteDB).where(
                and_(NoteDB.id == note_id, NoteDB.user_id == user_id)
            )
        )
        db_note = result.scalar_one_or_none()
        
        if not db_note:
            return None
        
        db_note.is_archived = not db_note.is_archived
        await db.commit()
        await db.refresh(db_note)
        
        return NoteResponse.model_validate(db_note)
    
    async def add_tag(self, db: AsyncSession, note_id: int, tag: str, user_id: int) -> Optional[NoteResponse]:
        """添加标签"""
        result = await db.execute(
            select(NoteDB).where(
                and_(NoteDB.id == note_id, NoteDB.user_id == user_id)
            )
        )
        db_note = result.scalar_one_or_none()
        
        if not db_note:
            return None
        
        if not db_note.tags:
            db_note.tags = []
        
        if tag not in db_note.tags:
            db_note.tags.append(tag)
            await db.commit()
            await db.refresh(db_note)
        
        return NoteResponse.model_validate(db_note)
    
    async def remove_tag(self, db: AsyncSession, note_id: int, tag: str, user_id: int) -> Optional[NoteResponse]:
        """移除标签"""
        result = await db.execute(
            select(NoteDB).where(
                and_(NoteDB.id == note_id, NoteDB.user_id == user_id)
            )
        )
        db_note = result.scalar_one_or_none()
        
        if not db_note:
            return None
        
        if db_note.tags and tag in db_note.tags:
            db_note.tags.remove(tag)
            await db.commit()
            await db.refresh(db_note)
        
        return NoteResponse.model_validate(db_note)
