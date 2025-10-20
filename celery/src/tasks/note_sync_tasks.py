"""
笔记同步 Celery 任务（独立 Celery 包）
"""

import logging
from typing import Dict, Any
from celery import current_task

from ..celery_app import celery_app
from .services.note_sync_service import note_sync_service

logger = logging.getLogger(__name__)


@celery_app.task(name="src.tasks.note_sync_tasks.sync_note_to_vector_db")
def sync_note_to_vector_db(note_id: int, user_id: int) -> Dict[str, Any]:
    try:
        current_task.update_state(state="PROGRESS", meta={"note_id": note_id, "user_id": user_id})
        success = note_sync_service.sync_note_to_vector_db(note_id, user_id)
        return {"note_id": note_id, "user_id": user_id, "status": "success" if success else "failed"}
    except Exception as e:
        logger.error(f"sync note error: {e}")
        current_task.update_state(state="FAILURE", meta={"error": str(e)})
        return {"status": "error", "message": str(e)}


@celery_app.task(name="src.tasks.note_sync_tasks.delete_note_from_vector_db")
def delete_note_from_vector_db(note_id: int, user_id: int) -> Dict[str, Any]:
    try:
        current_task.update_state(state="PROGRESS", meta={"note_id": note_id, "user_id": user_id})
        success = note_sync_service.delete_note_from_vector_db(note_id, user_id)
        return {"note_id": note_id, "user_id": user_id, "status": "success" if success else "failed"}
    except Exception as e:
        logger.error(f"delete note error: {e}")
        current_task.update_state(state="FAILURE", meta={"error": str(e)})
        return {"status": "error", "message": str(e)}


