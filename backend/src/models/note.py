from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class NoteCategoryEnum(str, Enum):
    """笔记分类枚举"""
    PERSONAL = "PERSONAL"
    WORK = "WORK"
    STUDY = "STUDY"
    IDEA = "IDEA"
    MEETING = "MEETING"
    OTHER = "OTHER"


class NoteBase(BaseModel):
    """笔记基础模型"""
    title: str = Field(..., min_length=1, max_length=255, description="笔记标题")
    content: str = Field(..., min_length=1, description="笔记内容")
    category: NoteCategoryEnum = Field(default=NoteCategoryEnum.PERSONAL, description="笔记分类")
    tags: Optional[List[str]] = Field(default=[], description="标签列表")
    is_pinned: bool = Field(default=False, description="是否置顶")
    is_archived: bool = Field(default=False, description="是否归档")


class NoteCreate(NoteBase):
    """创建笔记模型"""
    pass


class NoteUpdate(BaseModel):
    """更新笔记模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="笔记标题")
    content: Optional[str] = Field(None, min_length=1, description="笔记内容")
    category: Optional[NoteCategoryEnum] = Field(None, description="笔记分类")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    is_pinned: Optional[bool] = Field(None, description="是否置顶")
    is_archived: Optional[bool] = Field(None, description="是否归档")


class NoteResponse(NoteBase):
    """笔记响应模型"""
    id: int
    user_id: int
    word_count: int
    last_accessed: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    """笔记列表响应模型"""
    notes: List[NoteResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class NoteSearchRequest(BaseModel):
    """笔记搜索请求模型"""
    query: Optional[str] = Field(None, description="搜索关键词")
    category: Optional[NoteCategoryEnum] = Field(None, description="分类筛选")
    tags: Optional[List[str]] = Field(None, description="标签筛选")
    is_pinned: Optional[bool] = Field(None, description="是否置顶")
    is_archived: Optional[bool] = Field(None, description="是否归档")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    sort_by: str = Field(default="updated_at", description="排序字段")
    sort_order: str = Field(default="desc", description="排序方向")


class NoteStatsResponse(BaseModel):
    """笔记统计响应模型"""
    total_notes: int
    notes_by_category: dict
    total_words: int
    pinned_notes: int
    archived_notes: int
    recent_notes: int  # 最近7天创建的笔记数量
