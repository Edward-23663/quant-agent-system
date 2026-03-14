# 技能名称: atomic_sentiment_scraping
## 功能描述
基于语义向量检索 (RAG)，从本地知识库中召回与该标的相关的最新新闻、公告或社交媒体讨论文本。
## 入参格式 (JSON)
- ticker (str): 股票代码
- query (str): 检索词 (如 "贵州茅台 最新负面新闻 财务造假 业绩下滑")
- limit (int, 默认 10): 召回的文本片段数量
