# 技能名称: atomic_results_integration
## 功能描述
对来自不同分智能体的新闻、公告、参考链接等列表进行合并、基于 URL 或标题去重，并按照时间倒序排列。
## 入参格式 (JSON)
- source_lists (List[List[Dict]]): 多个来源的数据列表。每个 Dict 必须包含 `title`, `url` (可选), `date` (YYYY-MM-DD)。
