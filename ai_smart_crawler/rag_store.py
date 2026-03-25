"""
RAG集成模块 - 向量存储与检索
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# 尝试导入ChromaDB
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️ ChromaDB未安装，RAG功能将受限")

# 尝试导入OpenAI Embeddings
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class Document:
    """文档定义"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class RAGStore:
    """RAG存储 - 向量数据库管理"""
    
    def __init__(self, 
                 collection_name: str = "web_crawl_data",
                 openai_api_key: str = None,
                 persist_dir: str = "./chroma_db"):
        self.collection_name = collection_name
        self.openai_api_key = openai_api_key
        self.persist_dir = persist_dir
        
        self.client = None
        self.collection = None
        self.openai_client = None
        
        if CHROMADB_AVAILABLE:
            self._init_chroma()
        
        if OPENAI_AVAILABLE and openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=openai_api_key)
    
    def _init_chroma(self):
        """初始化ChromaDB"""
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"created": datetime.now().isoformat()}
            )
            print(f"✅ ChromaDB初始化成功: {self.collection_name}")
        except Exception as e:
            print(f"❌ ChromaDB初始化失败: {e}")
            self.client = None
    
    async def add_document(self, doc: Document) -> bool:
        """添加文档到向量库"""
        if not self.collection:
            print("⚠️ 向量库未初始化，跳过存储")
            return False
        
        # 生成embedding
        if not doc.embedding and self.openai_client:
            doc.embedding = await self._get_embedding(doc.content)
        
        try:
            self.collection.add(
                ids=[doc.id],
                documents=[doc.content],
                metadatas=[doc.metadata],
                embeddings=[doc.embedding] if doc.embedding else None
            )
            return True
        except Exception as e:
            print(f"❌ 添加文档失败: {e}")
            return False
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """语义搜索"""
        if not self.collection:
            return []
        
        try:
            # 生成查询embedding
            query_embedding = None
            if self.openai_client:
                query_embedding = await self._get_embedding(query)
            
            # 执行搜索
            results = self.collection.query(
                query_texts=[query],
                query_embeddings=[query_embedding] if query_embedding else None,
                n_results=top_k
            )
            
            # 格式化结果
            formatted = []
            for i in range(len(results['ids'][0])):
                formatted.append({
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
            
            return formatted
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []
    
    async def _get_embedding(self, text: str) -> List[float]:
        """获取文本embedding"""
        if not self.openai_client:
            return []
        
        try:
            response = await self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8000]  # 限制长度
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Embedding生成失败: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """获取存储统计"""
        if not self.collection:
            return {"status": "未初始化"}
        
        try:
            count = self.collection.count()
            return {
                "status": "正常",
                "document_count": count,
                "collection_name": self.collection_name,
                "persist_dir": self.persist_dir
            }
        except Exception as e:
            return {"status": f"错误: {e}"}


class CrawlKnowledgeBase:
    """爬取知识库 - 管理爬取的数据"""
    
    def __init__(self, openai_api_key: str = None):
        self.store = RAGStore(openai_api_key=openai_api_key) if CHROMADB_AVAILABLE else None
        self.documents_cache = []  # 内存缓存
    
    async def add_crawl_result(self, url: str, content: str, metadata: Dict = None):
        """添加爬取结果到知识库"""
        doc_id = self._generate_id(url)
        
        doc = Document(
            id=doc_id,
            content=content,
            metadata={
                "url": url,
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
        )
        
        # 存入向量库
        if self.store:
            await self.store.add_document(doc)
        
        # 内存缓存
        self.documents_cache.append(doc)
        
        print(f"✅ 已添加到知识库: {url}")
    
    async def query(self, question: str, top_k: int = 3) -> str:
        """基于知识库回答问题"""
        if not self.store:
            return "知识库未初始化"
        
        # 检索相关文档
        results = await self.store.search(question, top_k=top_k)
        
        if not results:
            return "未找到相关信息"
        
        # 构建上下文
        context = "\n\n".join([
            f"[来源: {r['metadata'].get('url', 'unknown')}]\n{r['content'][:500]}"
            for r in results
        ])
        
        return f"基于检索到的信息:\n\n{context}\n\n---\n问题: {question}"
    
    def _generate_id(self, url: str) -> str:
        """生成文档ID"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()
    
    def get_stats(self) -> Dict:
        """获取知识库统计"""
        return {
            "vector_store": self.store.get_stats() if self.store else {"status": "未启用"},
            "cache_count": len(self.documents_cache)
        }


async def rag_demo():
    """RAG演示"""
    print("\n" + "=" * 50)
    print("📚 RAG知识库演示")
    print("=" * 50)
    
    kb = CrawlKnowledgeBase()
    
    # 演示：添加模拟数据
    print("\n添加示例数据...")
    await kb.add_crawl_result(
        url="https://example.com/article1",
        content="脑肿瘤分割是医学图像处理的重要任务。U-Net架构在这方面表现出色。",
        metadata={"topic": "medical_imaging"}
    )
    await kb.add_crawl_result(
        url="https://example.com/article2",
        content="Transformer架构在医学图像分析中显示出巨大潜力，特别是在处理MRI数据时。",
        metadata={"topic": "medical_imaging"}
    )
    
    # 查询
    print("\n🔍 查询: 脑肿瘤分割用什么模型？")
    answer = await kb.query("脑肿瘤分割用什么模型？")
    print(answer)
    
    # 统计
    print("\n📊 知识库统计:")
    print(json.dumps(kb.get_stats(), indent=2))


if __name__ == "__main__":
    import asyncio
    asyncio.run(rag_demo())
