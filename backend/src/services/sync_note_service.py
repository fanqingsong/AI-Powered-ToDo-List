"""
同步版本的NoteService，用于在工具中调用
避免异步事件循环问题
"""

from typing import List, Optional
from sqlalchemy import select, delete, and_, or_, func, desc, asc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from datetime import datetime, timedelta

from ..models.note import NoteResponse, NoteCreate, NoteUpdate, NoteCategoryEnum
from ..models.database_models import NoteDB, NoteCategory
import os


class SyncNoteService:
    """
    同步版本的NoteService，用于在工具中调用
    避免异步事件循环问题
    """
    
    def __init__(self):
        # 创建同步数据库连接
        POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
        POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
        POSTGRES_DB = os.getenv("POSTGRES_DB", "ai_todo_db")
        POSTGRES_USER = os.getenv("POSTGRES_USER", "ai_todo_user")
        POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ai_todo_password")
        
        # 构建同步数据库URL
        SYNC_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        
        # 创建同步引擎
        self.engine = create_engine(
            SYNC_DATABASE_URL,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        # 创建会话工厂
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()
    
    def get_all_notes(self, user_id: Optional[int] = None) -> List[NoteResponse]:
        """获取所有笔记"""
        with self.get_session() as session:
            query = select(NoteDB)
            if user_id is not None:
                query = query.where(NoteDB.user_id == user_id)
            query = query.order_by(desc(NoteDB.updated_at))
            
            result = session.execute(query)
            notes_db = result.scalars().all()
            
            return [NoteResponse.model_validate(note) for note in notes_db]
    
    def get_note_by_id(self, note_id: int, user_id: Optional[int] = None) -> Optional[NoteResponse]:
        """根据ID获取笔记"""
        with self.get_session() as session:
            query = select(NoteDB).where(NoteDB.id == note_id)
            if user_id is not None:
                query = query.where(NoteDB.user_id == user_id)
            
            result = session.execute(query)
            note_db = result.scalar_one_or_none()
            
            if note_db:
                # 更新最后访问时间
                note_db.last_accessed = datetime.utcnow()
                session.commit()
                return NoteResponse.model_validate(note_db)
            return None
    
    def create_note(self, note_data: NoteCreate, user_id: Optional[int] = None) -> NoteResponse:
        """创建新笔记"""
        with self.get_session() as session:
            word_count = len(note_data.content)
            
            note_db = NoteDB(
                title=note_data.title,
                content=note_data.content,
                category=note_data.category.value,
                user_id=user_id,
                tags=note_data.tags or [],
                is_pinned=note_data.is_pinned,
                is_archived=note_data.is_archived,
                word_count=word_count
            )
            session.add(note_db)
            session.flush()
            session.commit()
            session.refresh(note_db)
            
            return NoteResponse.model_validate(note_db)
    
    def update_note(self, note_id: int, note_data: NoteUpdate, user_id: Optional[int] = None) -> Optional[NoteResponse]:
        """更新笔记"""
        with self.get_session() as session:
            query = select(NoteDB).where(NoteDB.id == note_id)
            if user_id is not None:
                query = query.where(NoteDB.user_id == user_id)
            
            result = session.execute(query)
            note_db = result.scalar_one_or_none()
            
            if not note_db:
                return None
            
            # 更新字段
            update_data = note_data.model_dump(exclude_unset=True)
            
            # 如果更新了内容，重新计算字数
            if 'content' in update_data:
                update_data['word_count'] = len(update_data['content'])
            
            # 如果更新了分类，需要转换枚举值
            if 'category' in update_data:
                update_data['category'] = update_data['category'].value
            
            for field, value in update_data.items():
                setattr(note_db, field, value)
            
            session.flush()
            session.commit()
            session.refresh(note_db)
            
            return NoteResponse.model_validate(note_db)
    
    def delete_note(self, note_id: int, user_id: Optional[int] = None) -> bool:
        """删除笔记"""
        with self.get_session() as session:
            query = delete(NoteDB).where(NoteDB.id == note_id)
            if user_id is not None:
                query = query.where(NoteDB.user_id == user_id)
            
            result = session.execute(query)
            session.commit()
            return result.rowcount > 0
    
    def get_note_by_title(self, title: str, user_id: Optional[int] = None) -> Optional[NoteResponse]:
        """根据标题模糊匹配获取笔记（如果有多个匹配笔记，返回第一个）"""
        with self.get_session() as session:
            query = select(NoteDB).where(NoteDB.title.like(f"%{title}%"))
            if user_id is not None:
                query = query.where(NoteDB.user_id == user_id)
            query = query.order_by(desc(NoteDB.updated_at)).limit(1)
            
            result = session.execute(query)
            note_db = result.scalar_one_or_none()
            
            if note_db:
                return NoteResponse.model_validate(note_db)
            return None
    
    def search_notes(
        self,
        query: Optional[str] = None,
        category: Optional[NoteCategoryEnum] = None,
        tags: Optional[List[str]] = None,
        is_pinned: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        user_id: Optional[int] = None,
        limit: int = 20
    ) -> List[NoteResponse]:
        """搜索笔记"""
        with self.get_session() as session:
            conditions = []
            if user_id is not None:
                conditions.append(NoteDB.user_id == user_id)
            
            # 关键词搜索
            if query:
                search_term = f"%{query}%"
                conditions.append(
                    or_(
                        NoteDB.title.ilike(search_term),
                        NoteDB.content.ilike(search_term)
                    )
                )
            
            # 分类筛选
            if category:
                conditions.append(NoteDB.category == category.value)
            
            # 标签筛选
            if tags:
                for tag in tags:
                    conditions.append(NoteDB.tags.contains([tag]))
            
            # 置顶筛选
            if is_pinned is not None:
                conditions.append(NoteDB.is_pinned == is_pinned)
            
            # 归档筛选
            if is_archived is not None:
                conditions.append(NoteDB.is_archived == is_archived)
            
            # 构建查询
            db_query = select(NoteDB)
            if conditions:
                db_query = db_query.where(and_(*conditions))
            db_query = db_query.order_by(desc(NoteDB.updated_at)).limit(limit)
            
            result = session.execute(db_query)
            notes_db = result.scalars().all()
            
            return [NoteResponse.model_validate(note) for note in notes_db]
    
    def get_pinned_notes(self, user_id: Optional[int] = None) -> List[NoteResponse]:
        """获取置顶笔记"""
        with self.get_session() as session:
            query = select(NoteDB).where(
                and_(
                    NoteDB.is_pinned == True,
                    NoteDB.is_archived == False
                )
            )
            if user_id is not None:
                query = query.where(NoteDB.user_id == user_id)
            query = query.order_by(desc(NoteDB.updated_at))
            
            result = session.execute(query)
            notes_db = result.scalars().all()
            
            return [NoteResponse.model_validate(note) for note in notes_db]
    
    def get_recent_notes(self, days: int = 7, limit: int = 20, user_id: Optional[int] = None) -> List[NoteResponse]:
        """获取最近笔记"""
        with self.get_session() as session:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            query = select(NoteDB).where(
                and_(
                    NoteDB.created_at >= since_date,
                    NoteDB.is_archived == False
                )
            )
            if user_id is not None:
                query = query.where(NoteDB.user_id == user_id)
            query = query.order_by(desc(NoteDB.created_at)).limit(limit)
            
            result = session.execute(query)
            notes_db = result.scalars().all()
            
            return [NoteResponse.model_validate(note) for note in notes_db]

