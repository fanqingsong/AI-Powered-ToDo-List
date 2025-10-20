"""
笔记同步任务
处理笔记与向量数据库的同步
"""

import logging
from typing import Dict, Any, Optional
from celery import current_task
from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker

from ..services.weaviate_client import weaviate_client
from ..models.database_models import NoteDB, UserDB
from ..models.note import NoteResponse
import os

logger = logging.getLogger(__name__)


class NoteSyncService:
    """笔记同步服务"""
    
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
    
    def get_note_by_id(self, note_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取笔记"""
        with self.get_session() as session:
            result = session.execute(
                select(NoteDB).where(
                    NoteDB.id == note_id,
                    NoteDB.user_id == user_id
                )
            )
            note_db = result.scalar_one_or_none()
            
            if note_db:
                return {
                    "id": note_db.id,
                    "user_id": note_db.user_id,
                    "title": note_db.title,
                    "content": note_db.content,
                    "category": note_db.category.value,
                    "tags": note_db.tags or [],
                    "is_pinned": note_db.is_pinned,
                    "is_archived": note_db.is_archived,
                    "word_count": note_db.word_count,
                    "created_at": note_db.created_at.isoformat(),
                    "updated_at": note_db.updated_at.isoformat()
                }
            return None
    
    def get_user_notes(self, user_id: int, limit: int = 100) -> list[Dict[str, Any]]:
        """获取用户的笔记列表"""
        with self.get_session() as session:
            result = session.execute(
                select(NoteDB).where(NoteDB.user_id == user_id).limit(limit)
            )
            notes_db = result.scalars().all()
            
            notes = []
            for note_db in notes_db:
                notes.append({
                    "id": note_db.id,
                    "user_id": note_db.user_id,
                    "title": note_db.title,
                    "content": note_db.content,
                    "category": note_db.category.value,
                    "tags": note_db.tags or [],
                    "is_pinned": note_db.is_pinned,
                    "is_archived": note_db.is_archived,
                    "word_count": note_db.word_count,
                    "created_at": note_db.created_at.isoformat(),
                    "updated_at": note_db.updated_at.isoformat()
                })
            
            return notes
    
    def sync_note_to_vector_db(self, note_id: int, user_id: int) -> bool:
        """同步单个笔记到向量数据库"""
        try:
            # 获取笔记数据
            note_data = self.get_note_by_id(note_id, user_id)
            if not note_data:
                logger.warning(f"未找到笔记 {note_id}，跳过同步")
                return False
            
            # 检查笔记是否已存在于向量数据库
            existing_note = weaviate_client.get_note_by_id(note_id, user_id)
            
            if existing_note:
                # 更新现有笔记
                weaviate_client.update_note(note_data)
                logger.info(f"成功更新笔记 {note_id} 到向量数据库")
            else:
                # 添加新笔记
                weaviate_client.add_note(note_data)
                logger.info(f"成功添加笔记 {note_id} 到向量数据库")
            
            return True
            
        except Exception as e:
            logger.error(f"同步笔记 {note_id} 到向量数据库失败: {e}")
            return False
    
    def sync_user_notes_to_vector_db(self, user_id: int) -> Dict[str, Any]:
        """同步用户所有笔记到向量数据库"""
        try:
            # 获取用户笔记
            notes = self.get_user_notes(user_id)
            
            success_count = 0
            failed_count = 0
            failed_notes = []
            
            for note in notes:
                try:
                    # 检查笔记是否已存在于向量数据库
                    existing_note = weaviate_client.get_note_by_id(note["id"], user_id)
                    
                    if existing_note:
                        # 更新现有笔记
                        weaviate_client.update_note(note)
                    else:
                        # 添加新笔记
                        weaviate_client.add_note(note)
                    
                    success_count += 1
                    logger.info(f"成功同步笔记 {note['id']}")
                    
                except Exception as e:
                    failed_count += 1
                    failed_notes.append(note["id"])
                    logger.error(f"同步笔记 {note['id']} 失败: {e}")
            
            result = {
                "user_id": user_id,
                "total_notes": len(notes),
                "success_count": success_count,
                "failed_count": failed_count,
                "failed_notes": failed_notes
            }
            
            logger.info(f"用户 {user_id} 笔记同步完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"同步用户 {user_id} 笔记失败: {e}")
            raise
    
    def delete_note_from_vector_db(self, note_id: int, user_id: int) -> bool:
        """从向量数据库中删除笔记"""
        try:
            success = weaviate_client.delete_note(note_id, user_id)
            if success:
                logger.info(f"成功从向量数据库中删除笔记 {note_id}")
            else:
                logger.warning(f"笔记 {note_id} 在向量数据库中不存在")
            return success
            
        except Exception as e:
            logger.error(f"从向量数据库中删除笔记 {note_id} 失败: {e}")
            return False


# 全局同步服务实例
note_sync_service = NoteSyncService()
