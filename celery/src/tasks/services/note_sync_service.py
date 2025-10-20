import os
from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker
from typing import Optional, Dict, Any, List

from .models import NoteDB
from .weaviate_client import weaviate_client


class NoteSyncService:
    def __init__(self):
        POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
        POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
        POSTGRES_DB = os.getenv("POSTGRES_DB", "ai_todo_db")
        POSTGRES_USER = os.getenv("POSTGRES_USER", "ai_todo_user")
        POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ai_todo_password")

        url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
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

    def sync_note_to_vector_db(self, note_id: int, user_id: int) -> bool:
        note = self.get_note(note_id, user_id)
        if not note:
            return False
        exist = weaviate_client.get_note_by_id(note_id, user_id)
        if exist:
            weaviate_client.update_note(note)
        else:
            weaviate_client.add_note(note)
        return True

    def delete_note_from_vector_db(self, note_id: int, user_id: int) -> bool:
        return weaviate_client.delete_note(note_id, user_id)


note_sync_service = NoteSyncService()


