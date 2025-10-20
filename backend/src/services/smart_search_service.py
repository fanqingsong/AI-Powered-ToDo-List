"""
智能搜索服务
提供基于向量数据库的智能搜索功能
"""

import logging
from typing import List, Dict, Any, Optional
from ..services.weaviate_client import weaviate_client
from ..models.note import NoteResponse, NoteCategoryEnum

logger = logging.getLogger(__name__)


class SmartSearchService:
    """智能搜索服务"""
    
    def __init__(self):
        self.weaviate_client = weaviate_client
    
    def search_notes(
        self,
        query: str,
        user_id: int,
        limit: int = 10,
        category: Optional[NoteCategoryEnum] = None,
        tags: Optional[List[str]] = None,
        include_archived: bool = False
    ) -> List[Dict[str, Any]]:
        """
        智能搜索笔记
        
        Args:
            query: 搜索查询
            user_id: 用户ID
            limit: 返回结果数量限制
            category: 笔记分类过滤
            tags: 标签过滤
            include_archived: 是否包含归档笔记
        
        Returns:
            搜索结果列表
        """
        try:
            logger.info(f"执行智能搜索: '{query}' for user {user_id}")
            
            # 构建搜索条件
            search_results = self.weaviate_client.search_notes(
                query=query,
                user_id=user_id,
                limit=limit,
                category=category.value if category else None,
                tags=tags
            )
            
            # 过滤归档笔记
            if not include_archived:
                search_results = [
                    note for note in search_results 
                    if not note.get("is_archived", False)
                ]
            
            # 转换为响应格式
            notes = []
            for note_data in search_results:
                try:
                    note = NoteResponse(
                        id=note_data["id"],
                        user_id=note_data["user_id"],
                        title=note_data["title"],
                        content=note_data["content"],
                        category=NoteCategoryEnum(note_data["category"]),
                        tags=note_data["tags"],
                        is_pinned=note_data["is_pinned"],
                        is_archived=note_data["is_archived"],
                        word_count=note_data["word_count"],
                        last_accessed=note_data.get("last_accessed", ""),
                        created_at=note_data["created_at"],
                        updated_at=note_data["updated_at"]
                    )
                    notes.append(note.model_dump())
                except Exception as e:
                    logger.warning(f"转换笔记数据失败: {e}")
                    continue
            
            logger.info(f"智能搜索完成，找到 {len(notes)} 个结果")
            return notes
            
        except Exception as e:
            logger.error(f"智能搜索失败: {e}")
            raise
    
    def get_similar_notes(
        self,
        note_id: int,
        user_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        获取相似笔记
        
        Args:
            note_id: 参考笔记ID
            user_id: 用户ID
            limit: 返回结果数量限制
        
        Returns:
            相似笔记列表
        """
        try:
            logger.info(f"获取笔记 {note_id} 的相似笔记")
            
            # 首先获取参考笔记
            reference_note = self.weaviate_client.get_note_by_id(note_id, user_id)
            if not reference_note:
                logger.warning(f"未找到笔记 {note_id}")
                return []
            
            # 使用笔记内容作为搜索查询
            search_query = f"{reference_note['title']} {reference_note['content']}"
            
            # 搜索相似笔记
            similar_notes = self.weaviate_client.search_notes(
                query=search_query,
                user_id=user_id,
                limit=limit + 1  # +1 因为会包含自己
            )
            
            # 过滤掉自己
            similar_notes = [
                note for note in similar_notes 
                if note["id"] != note_id
            ]
            
            # 限制结果数量
            similar_notes = similar_notes[:limit]
            
            # 转换为响应格式
            notes = []
            for note_data in similar_notes:
                try:
                    note = NoteResponse(
                        id=note_data["id"],
                        user_id=note_data["user_id"],
                        title=note_data["title"],
                        content=note_data["content"],
                        category=NoteCategoryEnum(note_data["category"]),
                        tags=note_data["tags"],
                        is_pinned=note_data["is_pinned"],
                        is_archived=note_data["is_archived"],
                        word_count=note_data["word_count"],
                        last_accessed=note_data.get("last_accessed", ""),
                        created_at=note_data["created_at"],
                        updated_at=note_data["updated_at"]
                    )
                    notes.append(note.model_dump())
                except Exception as e:
                    logger.warning(f"转换相似笔记数据失败: {e}")
                    continue
            
            logger.info(f"找到 {len(notes)} 个相似笔记")
            return notes
            
        except Exception as e:
            logger.error(f"获取相似笔记失败: {e}")
            raise
    
    def get_search_suggestions(
        self,
        query: str,
        user_id: int,
        limit: int = 5
    ) -> List[str]:
        """
        获取搜索建议
        
        Args:
            query: 搜索查询
            user_id: 用户ID
            limit: 返回结果数量限制
        
        Returns:
            搜索建议列表
        """
        try:
            logger.info(f"获取搜索建议: '{query}'")
            
            # 获取用户的笔记标题和标签
            user_notes = self.weaviate_client.get_all_notes(user_id)
            
            suggestions = set()
            
            # 从标题中提取建议
            for note in user_notes:
                title = note["title"].lower()
                if query.lower() in title:
                    suggestions.add(note["title"])
                
                # 从标签中提取建议
                for tag in note["tags"]:
                    if query.lower() in tag.lower():
                        suggestions.add(tag)
            
            # 转换为列表并排序
            suggestions = list(suggestions)[:limit]
            suggestions.sort(key=lambda x: len(x))  # 按长度排序
            
            logger.info(f"生成 {len(suggestions)} 个搜索建议")
            return suggestions
            
        except Exception as e:
            logger.error(f"获取搜索建议失败: {e}")
            return []
    
    def get_search_stats(self, user_id: int) -> Dict[str, Any]:
        """
        获取搜索统计信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            搜索统计信息
        """
        try:
            logger.info(f"获取用户 {user_id} 的搜索统计信息")
            
            # 获取用户笔记统计
            stats = self.weaviate_client.get_stats(user_id)
            
            # 添加搜索相关统计
            search_stats = {
                "total_notes": stats["total_notes"],
                "total_words": stats["total_words"],
                "pinned_notes": stats["pinned_notes"],
                "archived_notes": stats["archived_notes"],
                "category_stats": stats["category_stats"],
                "tag_stats": stats["tag_stats"],
                "search_enabled": True,
                "vector_db_status": "connected"
            }
            
            logger.info(f"搜索统计信息: {search_stats}")
            return search_stats
            
        except Exception as e:
            logger.error(f"获取搜索统计信息失败: {e}")
            return {
                "search_enabled": False,
                "vector_db_status": "error",
                "error": str(e)
            }
    
    def reindex_user_notes(self, user_id: int) -> Dict[str, Any]:
        """
        重新索引用户笔记
        
        Args:
            user_id: 用户ID
        
        Returns:
            重新索引结果
        """
        try:
            logger.info(f"开始重新索引用户 {user_id} 的笔记")
            
            # 获取用户所有笔记
            user_notes = self.weaviate_client.get_all_notes(user_id)
            
            # 删除现有索引
            for note in user_notes:
                try:
                    self.weaviate_client.delete_note(note["id"], user_id)
                except Exception as e:
                    logger.warning(f"删除笔记 {note['id']} 失败: {e}")
            
            # 重新添加所有笔记
            success_count = 0
            failed_count = 0
            
            for note in user_notes:
                try:
                    self.weaviate_client.add_note(note)
                    success_count += 1
                except Exception as e:
                    logger.error(f"重新索引笔记 {note['id']} 失败: {e}")
                    failed_count += 1
            
            result = {
                "user_id": user_id,
                "total_notes": len(user_notes),
                "success_count": success_count,
                "failed_count": failed_count,
                "status": "completed"
            }
            
            logger.info(f"重新索引完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"重新索引失败: {e}")
            return {
                "user_id": user_id,
                "status": "error",
                "message": str(e)
            }


# 全局智能搜索服务实例
smart_search_service = SmartSearchService()
