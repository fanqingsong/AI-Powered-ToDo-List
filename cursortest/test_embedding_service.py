#!/usr/bin/env python3
"""
测试自定义嵌入服务功能
"""

import os
import sys
import logging
from typing import List

# 添加项目路径
sys.path.append('/home/song/workspace/me/AI-Powered-ToDo-List/celery/src')

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_embedding_service():
    """测试嵌入服务"""
    try:
        from tasks.services.embedding_service import create_embedding_service
        
        # 测试不同提供商
        providers = ["openai", "cohere", "huggingface"]
        
        for provider in providers:
            logger.info(f"测试 {provider} 嵌入服务...")
            
            # 设置环境变量
            os.environ["EMBEDDING_PROVIDER"] = provider
            
            # 创建嵌入服务
            embedding_service = create_embedding_service()
            
            if embedding_service is None:
                logger.warning(f"{provider} 嵌入服务创建失败，跳过测试")
                continue
            
            # 测试文本嵌入
            test_texts = [
                "这是一个测试文本",
                "Hello, world!",
                "人工智能和机器学习"
            ]
            
            try:
                # 测试单个文本嵌入
                vector = embedding_service.embed_text(test_texts[0])
                logger.info(f"{provider} 单个文本嵌入成功，向量维度: {len(vector)}")
                
                # 测试批量文本嵌入
                vectors = embedding_service.embed_texts(test_texts)
                logger.info(f"{provider} 批量文本嵌入成功，向量数量: {len(vectors)}")
                
                # 测试笔记内容嵌入
                note_vector = embedding_service.embed_note_content(
                    "测试笔记标题", 
                    "这是一个测试笔记的内容，用于验证嵌入功能是否正常工作。"
                )
                logger.info(f"{provider} 笔记内容嵌入成功，向量维度: {len(note_vector)}")
                
                # 测试搜索查询嵌入
                query_vector = embedding_service.embed_search_query("搜索测试")
                logger.info(f"{provider} 搜索查询嵌入成功，向量维度: {len(query_vector)}")
                
                logger.info(f"{provider} 嵌入服务测试通过！")
                
            except Exception as e:
                logger.error(f"{provider} 嵌入服务测试失败: {e}")
            
            logger.info("-" * 50)
    
    except Exception as e:
        logger.error(f"嵌入服务测试失败: {e}")


def test_weaviate_client():
    """测试 Weaviate 客户端"""
    try:
        from tasks.services.weaviate_client import create_weaviate_client
        
        logger.info("测试 Weaviate 客户端...")
        
        # 创建客户端
        client = create_weaviate_client()
        
        # 测试连接
        if client.client.is_ready():
            logger.info("Weaviate 连接正常")
        else:
            logger.error("Weaviate 连接失败")
            return
        
        # 测试添加笔记
        test_note = {
            "id": 99999,
            "user_id": 1,
            "title": "测试笔记",
            "content": "这是一个测试笔记，用于验证自定义嵌入功能。",
            "category": "测试",
            "tags": ["测试", "嵌入"],
            "is_pinned": False,
            "is_archived": False,
            "word_count": 20,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        try:
            # 添加笔记
            result = client.add_note(test_note)
            logger.info(f"添加测试笔记成功: {result}")
            
            # 搜索笔记
            search_results = client.search_notes("测试", user_id=1, limit=5)
            logger.info(f"搜索测试笔记成功，找到 {len(search_results)} 条结果")
            
            # 删除测试笔记
            delete_result = client.delete_note(99999, 1)
            logger.info(f"删除测试笔记: {delete_result}")
            
            logger.info("Weaviate 客户端测试通过！")
            
        except Exception as e:
            logger.error(f"Weaviate 客户端操作失败: {e}")
    
    except Exception as e:
        logger.error(f"Weaviate 客户端测试失败: {e}")


def test_note_sync_service():
    """测试笔记同步服务"""
    try:
        from tasks.services.note_sync_service import note_sync_service
        
        logger.info("测试笔记同步服务...")
        
        # 测试获取笔记（需要数据库中有数据）
        try:
            note = note_sync_service.get_note(1, 1)
            if note:
                logger.info(f"获取笔记成功: {note['title']}")
            else:
                logger.info("未找到测试笔记，跳过同步测试")
                return
        except Exception as e:
            logger.info(f"获取笔记失败（可能数据库中没有数据）: {e}")
            return
        
        # 测试同步到向量数据库
        try:
            sync_result = note_sync_service.sync_note_to_vector_db(1, 1)
            logger.info(f"同步笔记到向量数据库: {sync_result}")
            
            logger.info("笔记同步服务测试通过！")
            
        except Exception as e:
            logger.error(f"笔记同步服务测试失败: {e}")
    
    except Exception as e:
        logger.error(f"笔记同步服务测试失败: {e}")


def main():
    """主测试函数"""
    logger.info("开始测试自定义嵌入服务功能...")
    logger.info("=" * 60)
    
    # 测试嵌入服务
    test_embedding_service()
    
    logger.info("=" * 60)
    
    # 测试 Weaviate 客户端
    test_weaviate_client()
    
    logger.info("=" * 60)
    
    # 测试笔记同步服务
    test_note_sync_service()
    
    logger.info("=" * 60)
    logger.info("测试完成！")


if __name__ == "__main__":
    main()
