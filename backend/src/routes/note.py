from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.database_models import UserDB
from ..models.note import (
    NoteCreate, NoteUpdate, NoteResponse, NoteListResponse,
    NoteSearchRequest, NoteStatsResponse, NoteCategoryEnum
)
from ..services.note_service import NoteService

router = APIRouter()
note_service = NoteService()


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建笔记"""
    try:
        note = await note_service.create_note(db, note_data, current_user.id)
        return note
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建笔记失败: {str(e)}"
        )


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取单个笔记"""
    note = await note_service.get_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记不存在"
        )
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_data: NoteUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新笔记"""
    note = await note_service.update_note(db, note_id, note_data, current_user.id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记不存在"
        )
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除笔记"""
    success = await note_service.delete_note(db, note_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记不存在"
        )


@router.post("/search", response_model=NoteListResponse)
async def search_notes(
    search_request: NoteSearchRequest,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """搜索笔记"""
    try:
        result = await note_service.search_notes(db, search_request, current_user.id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索笔记失败: {str(e)}"
        )


@router.get("/category/{category}", response_model=List[NoteResponse])
async def get_notes_by_category(
    category: NoteCategoryEnum,
    limit: int = Query(default=20, ge=1, le=100),
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """根据分类获取笔记"""
    try:
        notes = await note_service.get_notes_by_category(db, category, current_user.id, limit)
        return notes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分类笔记失败: {str(e)}"
        )


@router.get("/pinned/list", response_model=List[NoteResponse])
async def get_pinned_notes(
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取置顶笔记"""
    try:
        notes = await note_service.get_pinned_notes(db, current_user.id)
        return notes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取置顶笔记失败: {str(e)}"
        )


@router.get("/recent/list", response_model=List[NoteResponse])
async def get_recent_notes(
    days: int = Query(default=7, ge=1, le=30),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取最近笔记"""
    try:
        notes = await note_service.get_recent_notes(db, current_user.id, days, limit)
        return notes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取最近笔记失败: {str(e)}"
        )


@router.get("/stats/overview", response_model=NoteStatsResponse)
async def get_note_stats(
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取笔记统计信息"""
    try:
        stats = await note_service.get_note_stats(db, current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取笔记统计失败: {str(e)}"
        )


@router.patch("/{note_id}/pin", response_model=NoteResponse)
async def toggle_pin_note(
    note_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """切换笔记置顶状态"""
    note = await note_service.toggle_pin(db, note_id, current_user.id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记不存在"
        )
    return note


@router.patch("/{note_id}/archive", response_model=NoteResponse)
async def toggle_archive_note(
    note_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """切换笔记归档状态"""
    note = await note_service.toggle_archive(db, note_id, current_user.id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记不存在"
        )
    return note


@router.post("/{note_id}/tags", response_model=NoteResponse)
async def add_tag_to_note(
    note_id: int,
    tag: str = Query(..., min_length=1, max_length=50),
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """为笔记添加标签"""
    note = await note_service.add_tag(db, note_id, tag, current_user.id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记不存在"
        )
    return note


@router.delete("/{note_id}/tags", response_model=NoteResponse)
async def remove_tag_from_note(
    note_id: int,
    tag: str = Query(..., min_length=1, max_length=50),
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """从笔记移除标签"""
    note = await note_service.remove_tag(db, note_id, tag, current_user.id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记不存在"
        )
    return note


def create_note_routes():
    """创建笔记路由"""
    return router
