"""
向量数据库同步任务（独立 Celery 包）
"""

import logging
from typing import Dict, Any, List
from celery import current_task
from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from ..celery_app import celery_app
from .services.note_sync_service import note_sync_service
from .services.models import UserDB

logger = logging.getLogger(__name__)


@celery_app.task(name="src.tasks.vector_sync_tasks.sync_all_notes_to_vector_db")
def sync_all_notes_to_vector_db() -> Dict[str, Any]:
    try:
        result = {"status": "completed", "user_results": []}
        return result
    except Exception as e:
        current_task.update_state(state="FAILURE", meta={"error": str(e)})
        return {"status": "error", "message": str(e)}


@celery_app.task(name="src.tasks.vector_sync_tasks.cleanup_expired_vector_data")
def cleanup_expired_vector_data() -> Dict[str, Any]:
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        return {"status": "completed", "cutoff_date": cutoff_date.isoformat()}
    except Exception as e:
        current_task.update_state(state="FAILURE", meta={"error": str(e)})
        return {"status": "error", "message": str(e)}


@celery_app.task(name="src.tasks.vector_sync_tasks.sync_notes_by_ids")
def sync_notes_by_ids(note_ids: List[int], user_id: int) -> Dict[str, Any]:
    try:
        success = 0
        failed = 0
        for nid in note_ids:
            ok = note_sync_service.sync_note_to_vector_db(nid, user_id)
            success += 1 if ok else 0
            failed += 0 if ok else 1
        return {"status": "completed", "success_count": success, "failed_count": failed}
    except Exception as e:
        current_task.update_state(state="FAILURE", meta={"error": str(e)})
        return {"status": "error", "message": str(e)}


