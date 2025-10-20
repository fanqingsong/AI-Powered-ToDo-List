import os
from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker
from typing import Optional, Dict, Any, List

from .models import NoteDB
from .weaviate_client import create_weaviate_client


class NoteSyncService:
    def __init__(self):
        self.postgres_host = os.getenv("POSTGRES_HOST", "postgres")
        self.postgres_port = os.getenv("POSTGRES_PORT", "5432")
        self.postgres_db = os.getenv("POSTGRES_DB", "ai_todo_db")
        self.postgres_user = os.getenv("POSTGRES_USER", "ai_todo_user")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD", "ai_todo_password")

        url = f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        self.engine = create_engine(url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self):
        return self.SessionLocal()

    def get_note(self, note_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        with self.get_session() as session:
            result = session.execute(select(NoteDB).where(NoteDB.id == note_id, NoteDB.user_id == user_id))
            n = result.scalar_one_or_none()
            if not n:
                return None
            return {
                "id": n.id,
                "user_id": n.user_id,
                "title": n.title,
                "content": n.content,
                "category": n.category.value,
                "tags": n.tags or [],
                "is_pinned": n.is_pinned,
                "is_archived": n.is_archived,
                "word_count": n.word_count,
                "created_at": n.created_at.isoformat(),
                "updated_at": n.updated_at.isoformat(),
            }

    def get_user_notes(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户的所有笔记"""
        with self.get_session() as session:
            result = session.execute(select(NoteDB).where(NoteDB.user_id == user_id))
            notes = result.scalars().all()
            return [
                {
                    "id": n.id,
                    "user_id": n.user_id,
                    "title": n.title,
                    "content": n.content,
                    "category": n.category.value,
                    "tags": n.tags or [],
                    "is_pinned": n.is_pinned,
                    "is_archived": n.is_archived,
                    "word_count": n.word_count,
                    "created_at": n.created_at.isoformat(),
                    "updated_at": n.updated_at.isoformat(),
                }
                for n in notes
            ]

    def sync_note_to_vector_db(self, note_id: int, user_id: int) -> bool:
        """同步笔记到向量数据库（使用自定义嵌入服务）"""
        try:
            note = self.get_note(note_id, user_id)
            if not note:
                return False
            
            # 创建 Weaviate 客户端（使用自定义嵌入服务）
            weaviate_client = create_weaviate_client()
            
            # 检查笔记是否已存在
            exist = weaviate_client.get_note_by_id(note_id, user_id)
            if exist:
                weaviate_client.update_note(note)
            else:
                weaviate_client.add_note(note)
            
            return True
            
        except Exception as e:
            print(f"同步笔记 {note_id} 到向量数据库失败: {e}")
            return False

    def delete_note_from_vector_db(self, note_id: int, user_id: int) -> bool:
        """从向量数据库中删除笔记"""
        try:
            weaviate_client = create_weaviate_client()
            return weaviate_client.delete_note(note_id, user_id)
        except Exception as e:
            print(f"从向量数据库中删除笔记 {note_id} 失败: {e}")
            return False


note_sync_service = NoteSyncService()


