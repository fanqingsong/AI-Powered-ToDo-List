"""
智能搜索API路由
提供基于向量数据库的智能搜索功能
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.database_models import UserDB
from ..models.note import NoteResponse, NoteCategoryEnum
from ..services.smart_search_service import smart_search_service

router = APIRouter()


class SmartSearchRequest(BaseModel):
    """智能搜索请求"""
    query: str = Field(..., min_length=1, max_length=500, description="搜索查询")
    limit: int = Field(default=10, ge=1, le=50, description="返回结果数量限制")
    category: Optional[NoteCategoryEnum] = Field(default=None, description="笔记分类过滤")
    tags: Optional[List[str]] = Field(default=None, description="标签过滤")
    include_archived: bool = Field(default=False, description="是否包含归档笔记")


class SmartSearchResponse(BaseModel):
    """智能搜索响应"""
    notes: List[NoteResponse]
    total: int
    query: str
    suggestions: Optional[List[str]] = None


class SimilarNotesRequest(BaseModel):
    """相似笔记请求"""
    note_id: int = Field(..., description="参考笔记ID")
    limit: int = Field(default=5, ge=1, le=20, description="返回结果数量限制")


class SearchSuggestionsRequest(BaseModel):
    """搜索建议请求"""
    query: str = Field(..., min_length=1, max_length=100, description="搜索查询")
    limit: int = Field(default=5, ge=1, le=10, description="返回结果数量限制")


@router.post("/smart-search", response_model=SmartSearchResponse)
async def smart_search(
    search_request: SmartSearchRequest,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """智能搜索笔记"""
    try:
        # 执行智能搜索
        notes = smart_search_service.search_notes(
            query=search_request.query,
            user_id=current_user.id,
            limit=search_request.limit,
            category=search_request.category,
            tags=search_request.tags,
            include_archived=search_request.include_archived
        )
        
        # 获取搜索建议
        suggestions = smart_search_service.get_search_suggestions(
            query=search_request.query,
            user_id=current_user.id,
            limit=5
        )
        
        return SmartSearchResponse(
            notes=notes,
            total=len(notes),
            query=search_request.query,
            suggestions=suggestions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"智能搜索失败: {str(e)}"
        )


@router.post("/similar-notes", response_model=List[NoteResponse])
async def get_similar_notes(
    request: SimilarNotesRequest,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取相似笔记"""
    try:
        # 获取相似笔记
        notes = smart_search_service.get_similar_notes(
            note_id=request.note_id,
            user_id=current_user.id,
            limit=request.limit
        )
        
        return notes
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取相似笔记失败: {str(e)}"
        )


@router.post("/search-suggestions", response_model=List[str])
async def get_search_suggestions(
    request: SearchSuggestionsRequest,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取搜索建议"""
    try:
        # 获取搜索建议
        suggestions = smart_search_service.get_search_suggestions(
            query=request.query,
            user_id=current_user.id,
            limit=request.limit
        )
        
        return suggestions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取搜索建议失败: {str(e)}"
        )


@router.get("/search-stats")
async def get_search_stats(
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取搜索统计信息"""
    try:
        # 获取搜索统计
        stats = smart_search_service.get_search_stats(current_user.id)
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取搜索统计失败: {str(e)}"
        )


@router.post("/reindex")
async def reindex_user_notes(
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """重新索引用户笔记"""
    try:
        # 重新索引用户笔记
        result = smart_search_service.reindex_user_notes(current_user.id)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重新索引失败: {str(e)}"
        )


@router.get("/health")
async def search_health_check():
    """搜索服务健康检查"""
    try:
        # 检查向量数据库连接
        stats = smart_search_service.get_search_stats(1)  # 使用测试用户ID
        
        return {
            "status": "healthy",
            "vector_db_status": stats.get("vector_db_status", "unknown"),
            "search_enabled": stats.get("search_enabled", False)
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "vector_db_status": "error",
            "search_enabled": False
        }
