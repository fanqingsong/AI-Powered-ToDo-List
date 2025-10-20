"""
向量数据库同步任务（独立 Celery 包）
支持自定义嵌入服务
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
from .services.weaviate_client import create_weaviate_client

logger = logging.getLogger(__name__)


@celery_app.task(name="src.tasks.vector_sync_tasks.sync_all_notes_to_vector_db")
def sync_all_notes_to_vector_db() -> Dict[str, Any]:
    """同步所有笔记到向量数据库"""
    try:
        # 创建 Weaviate 客户端（使用自定义嵌入服务）
        weaviate_client = create_weaviate_client()
        
        result = {"status": "completed", "user_results": []}
        
        # 获取所有用户
        engine = create_engine(
            f"postgresql://{note_sync_service.postgres_user}:{note_sync_service.postgres_password}"
            f"@{note_sync_service.postgres_host}:{note_sync_service.postgres_port}/{note_sync_service.postgres_db}"
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as db:
            users = db.execute(select(UserDB)).scalars().all()
            
            for user in users:
                try:
                    # 获取用户的所有笔记
                    notes = note_sync_service.get_user_notes(user.id)
                    
                    synced_count = 0
                    for note in notes:
                        try:
                            # 同步笔记到向量数据库
                            note_sync_service.sync_note_to_vector_db(note.id, user.id)
                            synced_count += 1
                        except Exception as e:
                            logger.error(f"同步笔记 {note.id} 失败: {e}")
                    
                    result["user_results"].append({
                        "user_id": user.id,
                        "username": user.username,
                        "synced_count": synced_count,
                        "total_notes": len(notes)
                    })
                    
                except Exception as e:
                    logger.error(f"同步用户 {user.id} 的笔记失败: {e}")
                    result["user_results"].append({
                        "user_id": user.id,
                        "username": getattr(user, 'username', 'unknown'),
                        "error": str(e)
                    })
        
        logger.info(f"向量数据库同步完成: {result}")
        return result
        
    except Exception as e:
        logger.error(f"同步所有笔记到向量数据库失败: {e}")
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
    """同步指定笔记到向量数据库"""
    try:
        # 创建 Weaviate 客户端（使用自定义嵌入服务）
        weaviate_client = create_weaviate_client()
        
        success = 0
        failed = 0
        errors = []
        
        for note_id in note_ids:
            try:
                ok = note_sync_service.sync_note_to_vector_db(note_id, user_id)
                if ok:
                    success += 1
                else:
                    failed += 1
                    errors.append(f"笔记 {note_id} 同步失败")
            except Exception as e:
                failed += 1
                error_msg = f"笔记 {note_id} 同步异常: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        result = {
            "status": "completed", 
            "success_count": success, 
            "failed_count": failed,
            "errors": errors
        }
        
        logger.info(f"批量同步笔记完成: {result}")
        return result
        
    except Exception as e:
        logger.error(f"批量同步笔记失败: {e}")
        current_task.update_state(state="FAILURE", meta={"error": str(e)})
        return {"status": "error", "message": str(e)}


