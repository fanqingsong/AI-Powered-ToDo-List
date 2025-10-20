# Weaviate 多厂商嵌入模型支持方案

## 问题分析

当前项目只支持 OpenAI 的嵌入模型，限制了用户选择其他厂商嵌入模型的能力。

## 解决方案

### 方案一：使用 Weaviate 内置的其他厂商模块

#### 1. Cohere 支持

**Docker Compose 配置：**
```yaml
weaviate:
  image: semitechnologies/weaviate:1.24.10
  environment:
    - ENABLE_MODULES=text2vec-cohere,generative-cohere
    - DEFAULT_VECTORIZER_MODULE=text2vec-cohere
    - COHERE_APIKEY=${COHERE_API_KEY}
```

**Python 客户端配置：**
```python
# 创建类时使用 Cohere 向量化
note_class = {
    "class": "Note",
    "description": "笔记内容向量化存储",
    "vectorizer": "text2vec-cohere",
    "moduleConfig": {
        "text2vec-cohere": {
            "model": "embed-multilingual-v2.0",  # 或其他 Cohere 模型
            "truncate": "END"
        }
    },
    "properties": properties
}
```

#### 2. Hugging Face 支持

**Docker Compose 配置：**
```yaml
weaviate:
  image: semitechnologies/weaviate:1.24.10
  environment:
    - ENABLE_MODULES=text2vec-transformers,text2vec-huggingface
    - DEFAULT_VECTORIZER_MODULE=text2vec-transformers
    - TRANSFORMERS_CACHE_DIR=/tmp/transformers_cache
```

**Python 客户端配置：**
```python
# 使用 Hugging Face Transformers
note_class = {
    "class": "Note",
    "description": "笔记内容向量化存储",
    "vectorizer": "text2vec-transformers",
    "moduleConfig": {
        "text2vec-transformers": {
            "poolingStrategy": "masked_mean",
            "vectorizeClassName": False
        }
    },
    "properties": properties
}
```

### 方案二：自定义向量化（推荐）

这是最灵活的方案，支持任何厂商的嵌入模型。

#### 1. 修改 Docker Compose

```yaml
weaviate:
  image: semitechnologies/weaviate:1.24.10
  environment:
    - ENABLE_MODULES=generative-openai,qna-openai  # 移除 text2vec-openai
    - DEFAULT_VECTORIZER_MODULE=none  # 禁用自动向量化
```

#### 2. 创建自定义嵌入服务

```python
# services/embedding_service.py
from abc import ABC, abstractmethod
from typing import List
import openai
import requests
import numpy as np

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

class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI 嵌入模型提供者"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def embed_text(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [data.embedding for data in response.data]

class CohereEmbeddingProvider(EmbeddingProvider):
    """Cohere 嵌入模型提供者"""
    
    def __init__(self, api_key: str, model: str = "embed-multilingual-v2.0"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.cohere.ai/v1"
    
    def embed_text(self, text: str) -> List[float]:
        return self.embed_texts([text])[0]
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
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
            json=data
        )
        response.raise_for_status()
        
        result = response.json()
        return result["embeddings"]

class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    """Hugging Face 嵌入模型提供者"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._load_model()
    
    def _load_model(self):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(self.model_name)
    
    def embed_text(self, text: str) -> List[float]:
        return self.embed_texts([text])[0]
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

class EmbeddingService:
    """嵌入服务管理器"""
    
    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider
    
    def embed_note_content(self, title: str, content: str) -> List[float]:
        """为笔记内容生成嵌入向量"""
        # 组合标题和内容
        combined_text = f"{title}\n\n{content}"
        return self.provider.embed_text(combined_text)
    
    def embed_search_query(self, query: str) -> List[float]:
        """为搜索查询生成嵌入向量"""
        return self.provider.embed_text(query)
```

#### 3. 修改 WeaviateClient

```python
# 修改 weaviate_client.py
class WeaviateClient:
    def __init__(self, embedding_service: EmbeddingService = None):
        # ... 现有初始化代码 ...
        self.embedding_service = embedding_service
    
    def _create_note_class(self):
        """创建笔记类（禁用自动向量化）"""
        class_name = "Note"
        
        if self.client.schema.exists(class_name):
            logger.info(f"笔记类 '{class_name}' 已存在")
            return
        
        properties = [
            # ... 现有属性定义 ...
        ]
        
        # 禁用自动向量化
        note_class = {
            "class": class_name,
            "description": "笔记内容存储（自定义向量化）",
            "vectorizer": "none",  # 禁用自动向量化
            "properties": properties
        }
        
        try:
            self.client.schema.create_class(note_class)
            logger.info(f"成功创建笔记类 '{class_name}'")
        except Exception as e:
            logger.error(f"创建笔记类失败: {e}")
            raise
    
    def add_note(self, note_data: Dict[str, Any]) -> str:
        """添加笔记到向量数据库（使用自定义向量化）"""
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
                vector = self.embedding_service.embed_note_content(
                    note_data["title"], 
                    note_data["content"]
                )
                note_object["vector"] = vector
            
            # 添加到 Weaviate
            result = self.client.data_object.create(
                data_object=note_object,
                class_name="Note"
            )
            
            logger.info(f"成功添加笔记到向量数据库: {result}")
            return result
            
        except Exception as e:
            logger.error(f"添加笔记到向量数据库失败: {e}")
            raise
    
    def search_notes(self, query: str, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索笔记（使用自定义向量化）"""
        try:
            search_params = {
                "class": "Note",
                "where": {
                    "path": ["user_id"],
                    "operator": "Equal",
                    "valueInt": user_id
                },
                "limit": limit
            }
            
            # 如果有嵌入服务，使用向量搜索
            if self.embedding_service:
                query_vector = self.embedding_service.embed_search_query(query)
                search_params["nearVector"] = {
                    "vector": query_vector
                }
            else:
                # 使用文本搜索
                search_params["nearText"] = {
                    "concepts": [query]
                }
            
            result = self.client.query.get("Note", [
                "note_id", "user_id", "title", "content", 
                "category", "tags", "is_pinned", "is_archived",
                "word_count", "created_at", "updated_at"
            ]).with_near_vector(search_params["nearVector"]).with_where(
                search_params["where"]
            ).with_limit(limit).do()
            
            notes = []
            if "data" in result and "Get" in result["data"]:
                for item in result["data"]["Get"]["Note"]:
                    notes.append({
                        "id": item["note_id"],
                        "user_id": item["user_id"],
                        "title": item["title"],
                        "content": item["content"],
                        "category": item["category"],
                        "tags": item["tags"],
                        "is_pinned": item["is_pinned"],
                        "is_archived": item["is_archived"],
                        "word_count": item["word_count"],
                        "created_at": item["created_at"],
                        "updated_at": item["updated_at"]
                    })
            
            logger.info(f"找到 {len(notes)} 条相关笔记")
            return notes
            
        except Exception as e:
            logger.error(f"搜索笔记失败: {e}")
            raise
```

#### 4. 使用示例

```python
# 使用不同厂商的嵌入模型
from services.embedding_service import EmbeddingService, OpenAIEmbeddingProvider, CohereEmbeddingProvider

# OpenAI
openai_provider = OpenAIEmbeddingProvider(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="text-embedding-3-small"
)

# Cohere
cohere_provider = CohereEmbeddingProvider(
    api_key=os.getenv("COHERE_API_KEY"),
    model="embed-multilingual-v2.0"
)

# Hugging Face
hf_provider = HuggingFaceEmbeddingProvider(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 创建 Weaviate 客户端
embedding_service = EmbeddingService(openai_provider)  # 或其他提供商
weaviate_client = WeaviateClient(embedding_service)
```

## 环境变量配置

```bash
# .env 文件
# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Cohere
COHERE_API_KEY=your_cohere_api_key
COHERE_EMBEDDING_MODEL=embed-multilingual-v2.0

# Hugging Face
HF_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# 选择使用的嵌入提供商
EMBEDDING_PROVIDER=openai  # 或 cohere, huggingface
```

## 优势

1. **灵活性**：支持任何厂商的嵌入模型
2. **可扩展性**：易于添加新的嵌入提供商
3. **成本控制**：可以选择成本更低的嵌入模型
4. **性能优化**：可以根据需求选择最适合的模型
5. **离线支持**：Hugging Face 模型可以离线运行

## 注意事项

1. **向量维度**：不同模型的向量维度可能不同，需要确保一致性
2. **性能考虑**：自定义向量化会增加计算开销
3. **错误处理**：需要处理嵌入服务失败的情况
4. **缓存策略**：可以考虑缓存嵌入向量以提高性能
