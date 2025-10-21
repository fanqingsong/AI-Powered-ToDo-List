"""
Weaviate 向量数据库客户端
用于笔记内容的向量化存储和智能搜索
支持自定义嵌入服务
"""

import os
import weaviate
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WeaviateClient:
    """Weaviate 向量数据库客户端"""
    
    def __init__(self, embedding_service=None):
        """初始化 Weaviate 客户端"""
        self.host = os.getenv("WEAVIATE_HOST", "localhost")
        self.port = os.getenv("WEAVIATE_PORT", "8080")
        self.scheme = os.getenv("WEAVIATE_SCHEME", "http")
        
        # 构建连接URL
        self.url = f"{self.scheme}://{self.host}:{self.port}"
        
        # 创建客户端
        self.client = weaviate.Client(
            url=self.url,
            additional_headers={
                "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY", ""),
                "X-OpenAI-BaseURL": os.getenv("OPENAI_API_BASE", "")
            }
        )
        
        # 设置嵌入服务
        self.embedding_service = embedding_service
        
        # 确保连接正常
        self._ensure_connection()
        
        # 创建笔记类（如果不存在）
        self._create_note_class()
    
    def _ensure_connection(self):
        """确保 Weaviate 连接正常"""
        try:
            if not self.client.is_ready():
                raise Exception("Weaviate 服务未就绪")
            logger.info(f"成功连接到 Weaviate: {self.url}")
        except Exception as e:
            logger.error(f"连接 Weaviate 失败: {e}")
            raise
    
    def _create_note_class(self):
        """创建笔记类（支持自定义向量化）"""
        class_name = "Note"
        
        # 检查类是否已存在
        if self.client.schema.exists(class_name):
            logger.info(f"笔记类 '{class_name}' 已存在")
            return
        
        # 定义 properties 数组
        properties = [
            {
                "name": "note_id",
                "dataType": ["int"],
                "description": "笔记ID"
            },
            {
                "name": "user_id",
                "dataType": ["int"],
                "description": "用户ID"
            },
            {
                "name": "title",
                "dataType": ["text"],
                "description": "笔记标题"
            },
            {
                "name": "content",
                "dataType": ["text"],
                "description": "笔记内容"
            },
            {
                "name": "category",
                "dataType": ["text"],
                "description": "笔记分类"
            },
            {
                "name": "tags",
                "dataType": ["text[]"],
                "description": "笔记标签"
            },
            {
                "name": "is_pinned",
                "dataType": ["boolean"],
                "description": "是否置顶"
            },
            {
                "name": "is_archived",
                "dataType": ["boolean"],
                "description": "是否归档"
            },
            {
                "name": "word_count",
                "dataType": ["int"],
                "description": "字数统计"
            },
            {
                "name": "created_at",
                "dataType": ["date"],
                "description": "创建时间"
            },
            {
                "name": "updated_at",
                "dataType": ["date"],
                "description": "更新时间"
            },
            {
                "name": "last_synced_at",
                "dataType": ["date"],
                "description": "最后同步时间"
            }
        ]
        
        # 创建笔记类，禁用自动向量化
        note_class = {
            "class": class_name,
            "description": "笔记内容存储（自定义向量化）",
            "vectorizer": "none",  # 禁用自动向量化
            "properties": properties
        }
        
        try:
            self.client.schema.create_class(note_class)
            logger.info(f"成功创建笔记类 '{class_name}'（自定义向量化模式）")
        except Exception as e:
            logger.error(f"创建笔记类失败: {e}")
            raise
    
    def add_note(self, note_data: Dict[str, Any]) -> str:
        """添加笔记到向量数据库（支持自定义向量化）"""
        try:
            # 准备数据
            note_object = {
                "note_id": note_data["id"],
                "user_id": note_data["user_id"],
                "title": note_data["title"],
                "content": note_data["content"],
                "category": note_data["category"],
                "tags": note_data.get("tags", []),
                "is_pinned": note_data.get("is_pinned", False),
                "is_archived": note_data.get("is_archived", False),
                "word_count": note_data.get("word_count", 0),
                "created_at": note_data["created_at"],
                "updated_at": note_data["updated_at"],
                "last_synced_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
            
            # 生成向量（如果有嵌入服务）
            if self.embedding_service:
                try:
                    vector = self.embedding_service.embed_note_content(
                        note_data["title"], 
                        note_data["content"]
                    )
                    note_object["vector"] = vector
                    logger.debug(f"为笔记 {note_data['id']} 生成向量，维度: {len(vector)}")
                except Exception as e:
                    logger.error(f"生成笔记向量失败: {e}")
                    # 继续执行，但不包含向量
            else:
                logger.warning("未配置嵌入服务，将不生成向量")
            
            # 添加到 Weaviate
            result = self.client.data_object.create(
                data_object=note_object,
                class_name="Note"
            )
            
            logger.info(f"成功添加笔记到向量数据库: {note_data['id']}")
            return result
            
        except Exception as e:
            logger.error(f"添加笔记到向量数据库失败: {e}")
            raise
    
    def update_note(self, note_data: Dict[str, Any]) -> bool:
        """更新向量数据库中的笔记"""
        try:
            # 首先查找现有记录
            existing_objects = self.client.query.get(
                class_name="Note",
                properties=["note_id", "user_id"]
            ).with_where({
                "operator": "And",
                "operands": [
                    {
                        "path": ["note_id"],
                        "operator": "Equal",
                        "valueInt": note_data["id"]
                    },
                    {
                        "path": ["user_id"],
                        "operator": "Equal",
                        "valueInt": note_data["user_id"]
                    }
                ]
            }).with_additional(["id"]).do()
            
            if not existing_objects or "data" not in existing_objects or "Get" not in existing_objects["data"] or "Note" not in existing_objects["data"]["Get"] or not existing_objects["data"]["Get"]["Note"]:
                logger.warning(f"未找到笔记 {note_data['id']}，将创建新记录")
                self.add_note(note_data)
                return True
            
            # 获取现有对象的ID
            existing_object = existing_objects["data"]["Get"]["Note"][0]
            object_id = existing_object["_additional"]["id"]
            
            # 准备更新数据
            note_object = {
                "note_id": note_data["id"],
                "user_id": note_data["user_id"],
                "title": note_data["title"],
                "content": note_data["content"],
                "category": note_data["category"],
                "tags": note_data.get("tags", []),
                "is_pinned": note_data.get("is_pinned", False),
                "is_archived": note_data.get("is_archived", False),
                "word_count": note_data.get("word_count", 0),
                "created_at": note_data["created_at"],
                "updated_at": note_data["updated_at"],
                "last_synced_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
            
            # 生成新的向量（如果有嵌入服务）
            if self.embedding_service:
                try:
                    vector = self.embedding_service.embed_note_content(
                        note_data["title"], 
                        note_data["content"]
                    )
                    note_object["vector"] = vector
                    logger.debug(f"为笔记 {note_data['id']} 更新向量，维度: {len(vector)}")
                except Exception as e:
                    logger.error(f"生成更新向量失败: {e}")
                    # 继续执行，但不包含向量
            
            # 更新对象
            self.client.data_object.update(
                data_object=note_object,
                class_name="Note",
                uuid=object_id
            )
            
            logger.info(f"成功更新向量数据库中的笔记: {note_data['id']}")
            return True
            
        except Exception as e:
            logger.error(f"更新向量数据库中的笔记失败: {e}")
            raise
    
    def delete_note(self, note_id: int, user_id: int) -> bool:
        """从向量数据库中删除笔记"""
        try:
            # 查找要删除的记录
            existing_objects = self.client.query.get(
                class_name="Note",
                properties=["note_id", "user_id"]
            ).with_where({
                "operator": "And",
                "operands": [
                    {
                        "path": ["note_id"],
                        "operator": "Equal",
                        "valueInt": note_id
                    },
                    {
                        "path": ["user_id"],
                        "operator": "Equal",
                        "valueInt": user_id
                    }
                ]
            }).do()
            
            if not existing_objects["data"]["Get"]["Note"]:
                logger.warning(f"未找到要删除的笔记 {note_id}")
                return False
            
            # 获取对象ID并删除
            existing_object = existing_objects["data"]["Get"]["Note"][0]
            object_id = existing_object["_additional"]["id"]
            
            self.client.data_object.delete(
                class_name="Note",
                uuid=object_id
            )
            
            logger.info(f"成功从向量数据库中删除笔记: {note_id}")
            return True
            
        except Exception as e:
            logger.error(f"从向量数据库中删除笔记失败: {e}")
            raise
    
    def search_notes(self, query: str, user_id: int, limit: int = 10, 
                    category: Optional[str] = None, 
                    tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """智能搜索笔记"""
        try:
            # 构建搜索条件
            where_conditions = [
                {
                    "path": ["user_id"],
                    "operator": "Equal",
                    "valueInt": user_id
                }
            ]
            
            # 添加分类过滤
            if category:
                where_conditions.append({
                    "path": ["category"],
                    "operator": "Equal",
                    "valueText": category
                })
            
            # 添加标签过滤
            if tags:
                for tag in tags:
                    where_conditions.append({
                        "path": ["tags"],
                        "operator": "ContainsAny",
                        "valueText": [tag]
                    })
            
            # 执行搜索
            # ref： https://www.studywithgpt.com/zh-cn/tutorial/pvb8jo
            if self.embedding_service:
                # 使用自定义向量搜索
                try:
                    query_vector = self.embedding_service.embed_search_query(query)
                    result = self.client.query.get(
                        class_name="Note",
                        properties=[
                            "note_id", "user_id", "title", "content", 
                            "category", "tags", "is_pinned", "is_archived",
                            "word_count", "created_at", "updated_at"
                        ]
                    ).with_near_vector({
                        "vector": query_vector
                    }).with_where({
                        "operator": "And",
                        "operands": where_conditions
                    }).with_limit(limit).do()
                except Exception as e:
                    logger.error(f"自定义向量搜索失败: {e}")
                    # 回退到文本搜索
                    result = self.client.query.get(
                        class_name="Note",
                        properties=[
                            "note_id", "user_id", "title", "content", 
                            "category", "tags", "is_pinned", "is_archived",
                            "word_count", "created_at", "updated_at"
                        ]
                    ).with_near_text({
                        "concepts": [query]
                    }).with_where({
                        "operator": "And",
                        "operands": where_conditions
                    }).with_limit(limit).do()
            else:
                # 使用文本搜索（当没有嵌入服务时）
                result = self.client.query.get(
                    class_name="Note",
                    properties=[
                        "note_id", "user_id", "title", "content", 
                        "category", "tags", "is_pinned", "is_archived",
                        "word_count", "created_at", "updated_at"
                    ]
                ).with_near_text({
                    "concepts": [query]
                }).with_where({
                    "operator": "And",
                    "operands": where_conditions
                }).with_limit(limit).do()
            
            # 处理结果
            notes = []
            if result["data"]["Get"]["Note"]:
                for note in result["data"]["Get"]["Note"]:
                    notes.append({
                        "id": note["note_id"],
                        "user_id": note["user_id"],
                        "title": note["title"],
                        "content": note["content"],
                        "category": note["category"],
                        "tags": note["tags"],
                        "is_pinned": note["is_pinned"],
                        "is_archived": note["is_archived"],
                        "word_count": note["word_count"],
                        "created_at": note["created_at"],
                        "updated_at": note["updated_at"]
                    })
            
            logger.info(f"智能搜索完成，查询: '{query}'，结果数量: {len(notes)}")
            return notes
            
        except Exception as e:
            logger.error(f"智能搜索失败: {e}")
            raise
    
    def get_note_by_id(self, note_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取笔记"""
        try:
            result = self.client.query.get(
                class_name="Note",
                properties=[
                    "note_id", "user_id", "title", "content", 
                    "category", "tags", "is_pinned", "is_archived",
                    "word_count", "created_at", "updated_at"
                ]
            ).with_where({
                "operator": "And",
                "operands": [
                    {
                        "path": ["note_id"],
                        "operator": "Equal",
                        "valueInt": note_id
                    },
                    {
                        "path": ["user_id"],
                        "operator": "Equal",
                        "valueInt": user_id
                    }
                ]
            }).do()
            
            if result["data"]["Get"]["Note"]:
                note = result["data"]["Get"]["Note"][0]
                return {
                    "id": note["note_id"],
                    "user_id": note["user_id"],
                    "title": note["title"],
                    "content": note["content"],
                    "category": note["category"],
                    "tags": note["tags"],
                    "is_pinned": note["is_pinned"],
                    "is_archived": note["is_archived"],
                    "word_count": note["word_count"],
                    "created_at": note["created_at"],
                    "updated_at": note["updated_at"]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"根据ID获取笔记失败: {e}")
            raise
    
    def get_all_notes(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户的所有笔记"""
        try:
            result = self.client.query.get(
                class_name="Note",
                properties=[
                    "note_id", "user_id", "title", "content", 
                    "category", "tags", "is_pinned", "is_archived",
                    "word_count", "created_at", "updated_at"
                ]
            ).with_where({
                "path": ["user_id"],
                "operator": "Equal",
                "valueInt": user_id
            }).do()
            
            notes = []
            if result["data"]["Get"]["Note"]:
                for note in result["data"]["Get"]["Note"]:
                    notes.append({
                        "id": note["note_id"],
                        "user_id": note["user_id"],
                        "title": note["title"],
                        "content": note["content"],
                        "category": note["category"],
                        "tags": note["tags"],
                        "is_pinned": note["is_pinned"],
                        "is_archived": note["is_archived"],
                        "word_count": note["word_count"],
                        "created_at": note["created_at"],
                        "updated_at": note["updated_at"]
                    })
            
            return notes
            
        except Exception as e:
            logger.error(f"获取用户所有笔记失败: {e}")
            raise
    
    def get_stats(self, user_id: int) -> Dict[str, Any]:
        """获取用户笔记统计信息"""
        try:
            # 获取所有笔记
            all_notes = self.get_all_notes(user_id)
            
            # 统计信息
            stats = {
                "total_notes": len(all_notes),
                "total_words": sum(note["word_count"] for note in all_notes),
                "pinned_notes": len([note for note in all_notes if note["is_pinned"]]),
                "archived_notes": len([note for note in all_notes if note["is_archived"]]),
                "category_stats": {},
                "tag_stats": {}
            }
            
            # 分类统计
            for note in all_notes:
                category = note["category"]
                stats["category_stats"][category] = stats["category_stats"].get(category, 0) + 1
            
            # 标签统计
            for note in all_notes:
                for tag in note["tags"]:
                    stats["tag_stats"][tag] = stats["tag_stats"].get(tag, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"获取笔记统计信息失败: {e}")
            raise


def create_weaviate_client() -> WeaviateClient:
    """创建 WeaviateClient 实例"""
    try:
        # 导入嵌入服务
        from .embedding_service import create_embedding_service
        
        # 创建嵌入服务
        embedding_service = create_embedding_service()
        
        # 创建 WeaviateClient
        client = WeaviateClient(embedding_service)
        
        logger.info("成功创建 WeaviateClient 实例")
        return client
        
    except Exception as e:
        logger.error(f"创建 WeaviateClient 失败: {e}")
        # 返回没有嵌入服务的客户端
        return WeaviateClient()


# 全局 Weaviate 客户端实例
weaviate_client = create_weaviate_client()


