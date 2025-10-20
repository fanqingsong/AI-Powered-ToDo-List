"""
Celery 客户端（后端轻依赖）。
通过 task name 发送任务，避免直接导入任务模块，降低耦合。
"""

import os
from typing import Any, List
from celery import Celery
import logging

logger = logging.getLogger(__name__)


def _get_celery_app() -> Celery:
    host = os.getenv("REDIS_HOST", "redis")
    port = os.getenv("REDIS_PORT", "6379")
    db = os.getenv("REDIS_DB", "0")
    broker = f"redis://{host}:{port}/{db}"
    backend = broker
    app = Celery("ai_todo_client", broker=broker, backend=backend)
    return app


def _send_task(task_name: str, args: List[Any]) -> None:
    try:
        app = _get_celery_app()
        app.send_task(task_name, args=args)
        logger.info(f"Celery task dispatched: {task_name} args={args}")
    except Exception as e:
        logger.error(f"Failed to dispatch celery task {task_name}: {e}")


def enqueue_sync_note(note_id: int, user_id: int) -> None:
    _send_task("src.tasks.note_sync_tasks.sync_note_to_vector_db", [note_id, user_id])


def enqueue_delete_note(note_id: int, user_id: int) -> None:
    _send_task("src.tasks.note_sync_tasks.delete_note_from_vector_db", [note_id, user_id])


