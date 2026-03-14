# core/vector_store.py
import os
import uuid
import logging
from typing import List, Dict, Any
import lancedb
from fastembed import TextEmbedding

logger = logging.getLogger(__name__)

class VectorStore:
    """
    轻量级本地向量知识库
    基于 LanceDB (存储) + FastEmbed (本地 CPU 向量化)
    """
    def __init__(self, 
                 db_path: str = "data/db/vector_index.lance", 
                 collection_name: str = "financial_docs",
                 embed_model: str = "BAAI/bge-small-zh-v1.5"):
        
        self.db_path = db_path
        self.collection_name = collection_name
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 连接 LanceDB
        self.db = lancedb.connect(self.db_path)
        
        # 初始化本地 Embedding 模型 (全量在本地 CPU 运行，无需 API Key)
        # BAAI/bge-small-zh-v1.5 是目前非常优秀的中文轻量级向量模型
        logger.info(f"正在加载本地 Embedding 模型 {embed_model} (首次运行需下载权重)...")
        self.embedding_model = TextEmbedding(model_name=embed_model)
        
        self._init_collection()

    def _init_collection(self):
        """初始化 Collection，如果不存在则创建（依赖第一次插入的数据推断 Schema）"""
        if self.collection_name not in self.db.table_names():
            logger.info(f"向量集合 {self.collection_name} 不存在，将在首次插入数据时自动创建。")

    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        """
        将文本切片及其元数据向量化并存入 LanceDB
        :param texts: 文本切片列表 (如 ["茅台2023年营收增长15%", ...])
        :param metadatas: 对应的元数据 (如 [{"ticker": "600519.SH", "source": "news"}, ...])
        """
        if len(texts) != len(metadatas):
            raise ValueError("Texts 和 Metadatas 的长度必须一致。")

        # 1. 本地生成向量
        logger.info(f"正在向量化 {len(texts)} 条文本...")
        embeddings_generator = self.embedding_model.embed(texts)
        embeddings = list(embeddings_generator)

        # 2. 构造 LanceDB 所需的 List[Dict] 格式
        data = []
        for i in range(len(texts)):
            row = {
                "id": str(uuid.uuid4()),
                "vector": embeddings[i],
                "text": texts[i],
                **metadatas[i]  # 展开元数据字段 (如 ticker, date)
            }
            data.append(row)

        # 3. 插入或创建表
        if self.collection_name in self.db.table_names():
            tbl = self.db.open_table(self.collection_name)
            tbl.add(data)
        else:
            self.db.create_table(self.collection_name, data=data)
            
        logger.info(f"成功将 {len(texts)} 条文档存入向量库。")

    def search(self, query: str, limit: int = 5, where_clause: str = None) -> List[Dict[str, Any]]:
        """
        语义检索 Top-K 相关的文本片段
        :param query: 用户问题或检索词
        :param limit: 返回数量限制
        :param where_clause: SQL 风格的元数据过滤条件 (如 "ticker = '600519.SH'")
        """
        if self.collection_name not in self.db.table_names():
            return []

        # 1. 将 Query 向量化
        query_vector = list(self.embedding_model.embed([query]))[0]

        # 2. 执行向量相似度检索
        tbl = self.db.open_table(self.collection_name)
        search_builder = tbl.search(query_vector).limit(limit)
        
        # 3. 增加标的/时间等元数据过滤 (混合检索)
        if where_clause:
            search_builder = search_builder.where(where_clause)

        # 4. 转换为普通的 Dict 列表返回
        results = search_builder.to_list()
        
        # 剔除不必要的 vector 字段以减轻打印或传输负担
        for r in results:
            r.pop("vector", None)
            
        return results
