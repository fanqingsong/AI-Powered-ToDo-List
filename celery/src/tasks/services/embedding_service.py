"""
自定义嵌入服务模块
支持多种厂商的嵌入模型，包括 OpenAI、Cohere、Hugging Face 等
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """嵌入模型提供者抽象基类"""
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """将文本转换为向量"""
        pass
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量将文本转换为向量"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI 嵌入模型提供者"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small", base_url: str = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or "https://api.openai.com/v1"
        
        # 验证 API Key
        if not self.api_key:
            raise ValueError("OpenAI API Key 不能为空")
    
    def embed_text(self, text: str) -> List[float]:
        """将单个文本转换为向量"""
        try:
            response = requests.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "input": text
                },
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result["data"][0]["embedding"]
            
        except Exception as e:
            logger.error(f"OpenAI 嵌入失败: {e}")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量将文本转换为向量"""
        try:
            response = requests.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "input": texts
                },
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return [item["embedding"] for item in result["data"]]
            
        except Exception as e:
            logger.error(f"OpenAI 批量嵌入失败: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": "openai",
            "model": self.model,
            "base_url": self.base_url,
            "max_tokens": 8191,  # text-embedding-3-small 的最大 token 数
            "dimensions": 1536    # text-embedding-3-small 的向量维度
        }


class CohereEmbeddingProvider(EmbeddingProvider):
    """Cohere 嵌入模型提供者"""
    
    def __init__(self, api_key: str, model: str = "embed-multilingual-v2.0"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.cohere.ai/v1"
        
        # 验证 API Key
        if not self.api_key:
            raise ValueError("Cohere API Key 不能为空")
    
    def embed_text(self, text: str) -> List[float]:
        """将单个文本转换为向量"""
        return self.embed_texts([text])[0]
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量将文本转换为向量"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "texts": texts,
                "model": self.model,
                "truncate": "END"
            }
            
            response = requests.post(
                f"{self.base_url}/embed",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result["embeddings"]
            
        except Exception as e:
            logger.error(f"Cohere 嵌入失败: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": "cohere",
            "model": self.model,
            "base_url": self.base_url,
            "max_tokens": 512,  # Cohere 模型的最大 token 数
            "dimensions": 768   # embed-multilingual-v2.0 的向量维度
        }


class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    """Hugging Face 嵌入模型提供者"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", api_key: str = None):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = "https://api-inference.huggingface.co/models"
        self.model = None
        
        # 延迟加载模型
        self._load_model()
    
    def _load_model(self):
        """加载 Hugging Face 模型"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"成功加载 Hugging Face 模型: {self.model_name}")
        except ImportError:
            logger.warning("sentence-transformers 未安装，将使用 API 模式")
            self.model = None
        except Exception as e:
            logger.error(f"加载 Hugging Face 模型失败: {e}")
            self.model = None
    
    def embed_text(self, text: str) -> List[float]:
        """将单个文本转换为向量"""
        return self.embed_texts([text])[0]
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量将文本转换为向量"""
        if self.model is not None:
            # 使用本地模型
            try:
                embeddings = self.model.encode(texts)
                return embeddings.tolist()
            except Exception as e:
                logger.error(f"Hugging Face 本地模型嵌入失败: {e}")
                raise
        else:
            # 使用 API
            try:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                response = requests.post(
                    f"{self.base_url}/{self.model_name}",
                    headers=headers,
                    json={"inputs": texts},
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result
                else:
                    raise ValueError("API 返回格式不正确")
                    
            except Exception as e:
                logger.error(f"Hugging Face API 嵌入失败: {e}")
                raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": "huggingface",
            "model": self.model_name,
            "base_url": self.base_url,
            "max_tokens": 256,  # 大多数 sentence-transformers 模型的最大 token 数
            "dimensions": 384,  # all-MiniLM-L6-v2 的向量维度
            "local_model": self.model is not None
        }


class EmbeddingService:
    """嵌入服务管理器"""
    
    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider
        self.model_info = provider.get_model_info()
        logger.info(f"初始化嵌入服务: {self.model_info}")
    
    def embed_note_content(self, title: str, content: str) -> List[float]:
        """为笔记内容生成嵌入向量"""
        try:
            # 组合标题和内容
            combined_text = f"{title}\n\n{content}"
            
            # 检查文本长度
            max_tokens = self.model_info.get("max_tokens", 1000)
            if len(combined_text) > max_tokens * 4:  # 粗略估算，1 token ≈ 4 字符
                logger.warning(f"文本长度超过模型限制，将截断")
                combined_text = combined_text[:max_tokens * 4]
            
            return self.provider.embed_text(combined_text)
            
        except Exception as e:
            logger.error(f"生成笔记嵌入向量失败: {e}")
            raise
    
    def embed_search_query(self, query: str) -> List[float]:
        """为搜索查询生成嵌入向量"""
        try:
            return self.provider.embed_text(query)
        except Exception as e:
            logger.error(f"生成搜索查询嵌入向量失败: {e}")
            raise
    
    def embed_texts_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成嵌入向量"""
        try:
            return self.provider.embed_texts(texts)
        except Exception as e:
            logger.error(f"批量生成嵌入向量失败: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return self.model_info


def create_embedding_service(provider_name: str = None) -> Optional[EmbeddingService]:
    """创建嵌入服务实例"""
    try:
        # 从环境变量获取提供商名称
        provider_name = provider_name or os.getenv("EMBEDDING_PROVIDER", "openai")
        
        if provider_name.lower() == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
            base_url = os.getenv("OPENAI_API_BASE")
            
            if not api_key:
                logger.warning("未设置 OPENAI_API_KEY，跳过嵌入服务初始化")
                return None
            
            provider = OpenAIEmbeddingProvider(api_key, model, base_url)
            
        elif provider_name.lower() == "cohere":
            api_key = os.getenv("COHERE_API_KEY")
            model = os.getenv("COHERE_EMBEDDING_MODEL", "embed-multilingual-v2.0")
            
            if not api_key:
                logger.warning("未设置 COHERE_API_KEY，跳过嵌入服务初始化")
                return None
            
            provider = CohereEmbeddingProvider(api_key, model)
            
        elif provider_name.lower() == "huggingface":
            model_name = os.getenv("HF_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
            api_key = os.getenv("HUGGINGFACE_API_KEY")
            
            provider = HuggingFaceEmbeddingProvider(model_name, api_key)
            
        else:
            logger.error(f"不支持的嵌入提供商: {provider_name}")
            return None
        
        return EmbeddingService(provider)
        
    except Exception as e:
        logger.error(f"创建嵌入服务失败: {e}")
        return None
