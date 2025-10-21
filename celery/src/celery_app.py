"""
Celery 应用配置（独立于后端 backend）。
"""

import os
from celery import Celery
from celery.schedules import crontab


REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")

BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

celery_app = Celery(
    "ai_todo_celery",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=[
        "src.tasks.note_sync_tasks",
        "src.tasks.vector_sync_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "src.tasks.note_sync_tasks.*": {"queue": "note_sync"},
        "src.tasks.vector_sync_tasks.*": {"queue": "vector_sync"},
    },
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    # Celery Beat 定时任务调度配置
    beat_schedule={
        # 每小时整点同步所有用户笔记到向量数据库
        "sync-notes-to-vector-db": {
            "task": "src.tasks.vector_sync_tasks.sync_all_notes_to_vector_db",
            "schedule": crontab(minute=0),
        },
        # 每天凌晨2点清理过期向量数据
        "cleanup-expired-vector-data": {
            "task": "src.tasks.vector_sync_tasks.cleanup_expired_vector_data",
            "schedule": crontab(hour=2, minute=0),
        },
    },
    result_expires=86400,  # 24小时过期，让 Flower 能看到任务历史
    task_soft_time_limit=300,
    task_time_limit=600,
)

if __name__ == "__main__":
    celery_app.start()


